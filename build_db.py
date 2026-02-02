import sqlite3
import pandas as pd
import os
import re
from datetime import datetime
from utility_maps import LAND_DATA_MAP
# Add this to your existing imports
from sync_git import sync_to_github

# --- CONFIGURATION ---
DB_PATH = os.path.join("data", "mtg_pauper.db")
DATA_DIR = "data"
CLASSIFICATION_DIR = "data" 
DECKS_DIR = os.path.join("data", "decks")

def rename_cols(df):
    df.rename(columns={
        'Count': 'qty',
        'Qty': 'qty',
        'Name': 'name',
        'Edition': 'edition',
        'Type': 'type',
        'Rarity': 'rarity',
        'Price': 'price',
        'Section': 'section',
        'Image URL': 'image_url',
        'Scryfall ID': 'scryfall_id',
        'Code': 'code',
        'Total': 'total_cards_value',
        'MatchName': 'name_match',
        'Cost': 'mana',
        'Thumbnail': 'bb_deck_img',
        'Mana': 'mana',
        'NumForBuild': 'num_for_deck'
    }, inplace=True, errors='ignore')
    return df

def get_match_name(name):
    if not isinstance(name, str): return ""
    name = re.sub(r'\(.*?\)|\[.*?\]', '', name)
    return name.lower().strip()


def get_latest_file(directory, pattern):
    if not os.path.exists(directory): return None
    files = [f for f in os.listdir(directory) if re.search(pattern, f) and f.endswith(".csv")]
    if not files: return None

    def extract_date(filename):
        match = re.search(r"(\d{4})\.(\w+)\.(\d{1,2})", filename)
        if match:
            try: return datetime.strptime(f"{match.group(1)} {match.group(2)} {match.group(3)}", "%Y %B %d")
            except: return datetime.min
        return datetime.min
    
    # Sort files by date descending
    files.sort(key=extract_date, reverse=True)
    latest_file = files[0]
    
    sync_github = False
    # --- DELETE OLDER VERSIONS ---
    if len(files) > 1:
        for old_file in files[1:]:
            try:
                sync_github = True
                os.remove(os.path.join(directory, old_file))
                print(f"🗑️ Deleted old version: {old_file}")
            except Exception as e:
                print(f"⚠️ Could not delete {old_file}: {e}")

    return os.path.join(directory, latest_file), sync_github
    

def clean_inventory(path):
    df = pd.read_csv(path)
    df['Edition Code'] = df['Edition Code'].astype(str).str.strip().fillna('')
    df['Card Number'] = df['Card Number'].astype(str).str.strip().fillna('')
    df['Code'] = df['Edition Code'] + " - " + df['Card Number']
    
    df['Price'] = df['Price'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0.00)
    df['Count'] = pd.to_numeric(df['Count'], errors='coerce').fillna(0).astype(int)
    df['Total'] = df['Count'] * df['Price']
    df['MatchName'] = df['Name'].apply(get_match_name)

    drop_cols = ['Tradelist Count', 'Decks Count Built', 'Decks Count All', 'Condition', 'Language', 'Foil', 'Signed', 'Artist Proof', 'Altered Art', 'Misprint', 'Promo', 'Textless', 'Printing Id','Printing Note', 'Tags', 'My Price', 'Last Updated', 'TcgPlayer ID']
    df.drop(columns=drop_cols, inplace=True, errors='ignore')
    return df


def load_all_decks_cards(path):
    if not os.path.exists(path): return pd.DataFrame(), False

    all_deck_data = []
    files = [f for f in os.listdir(path) if f.endswith(".csv")]

    if not files: return pd.DataFrame(), False

    prefixes = set(re.split(r'_mikelele', f)[0] for f in files)
    
    any_new_deck = False
    for prefix in prefixes:

        latest_deck, status = get_latest_file(path, rf"^{re.escape(prefix)}_mikelele")
        
        if status: any_new_deck = True
        if latest_deck:
            df = pd.read_csv(latest_deck)
            df['DeckName'] = prefix.strip()
            df['Price'] = df['Price'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0.00)
            df['Count'] = pd.to_numeric(df.get('Count', df.get('Qty', 0)), errors='coerce').fillna(0).astype(int)
            df['Total'] = df['Count'] * df['Price']
            df['MatchName'] = df['Name'].apply(get_match_name)
            df.drop(['Last Updated', 'TcgPlayer ID'], axis=1, inplace=True, errors='ignore')
            all_deck_data.append(df)

        final_df = pd.concat(all_deck_data, ignore_index=True) if all_deck_data else pd.DataFrame()
    return final_df, any_new_deck


def calculate_priority_buildability(df_inventory, df_all_decks, df_bb):
    virtual_inv = df_inventory.groupby('MatchName')['Count'].sum().to_dict()
    df_bb = df_bb.copy()
    allocations = []
    
    main_completion, side_completion = [], []

    for _, row in df_bb.iterrows():
        deck_name = row['DeckName'].strip()
        
        def get_pct(section_name):
            cards = df_all_decks[(df_all_decks['DeckName'] == deck_name) & (df_all_decks['Section'].str.contains(section_name, case=False, na=False))]
            total = cards['Count'].sum()
            if total == 0: return 100
            acquired = 0
            for _, card in cards.iterrows():
                m_name, needed = card['MatchName'], card['Count']
                available = virtual_inv.get(m_name, 0)
                taken = min(needed, available)
                allocations.append({'DeckName': deck_name, 'MatchName': m_name, 'Section': card['Section'], 'NumForBuild': taken})
                acquired += taken
                virtual_inv[m_name] = available - taken
            return int((acquired / total) * 100)

        main_completion.append(get_pct('Main'))
        side_completion.append(get_pct('Side'))

    df_bb['CompletionPct'] = main_completion  
    df_bb['SideboardPct'] = side_completion

    df_allocs = pd.DataFrame(allocations)
    updated_all_decks = df_all_decks.merge(df_allocs, on=['DeckName', 'MatchName', 'Section'], how='left').fillna({'NumForBuild': 0})
    return df_bb, updated_all_decks


def get_card_cmc_and_color(df):
    pattern = r'\{(.*?)\}'
    color_map = {'W':'W', 'U':'U', 'B':'B', 'R':'R', 'G':'G'}
    cmcs, colors, is_multi_colored = [], [], []

    df = df.copy()

    for _, row in df.iterrows():
        mana_str = str(row.get('Cost', '')).strip()
        type_line = str(row.get('Type', ''))
        
        # Default values for Lands
        if "Land" in type_line:
            cmc_val = 0
            final_color = "L" # 'L' keeps them out of the 'C' (Colorless) slice
            multi_color = False
        else:
            # 1. CMC Calculation
            parts = mana_str.split('//')
            parts_cmc = []
            for p in parts:
                symbols = re.findall(pattern, p)
                val = sum(int(s) if s.isdigit() else (0 if s.upper() == 'X' else 1) for s in symbols if s)
                parts_cmc.append(val)
            cmc_val = parts_cmc[0] if parts_cmc else 0
            
            # 2. Color Classification
            all_syms = re.findall(pattern, mana_str)
            found_colors = "".join(sorted(list({color_map[c] for s in all_syms for c in color_map if c in s.upper()})))
            
            if len(found_colors) == 0:
                final_color = "C"
                multi_color = False
            else:
                if len(found_colors) == 1:
                    final_color = str(found_colors)
                    multi_color = False
                else:
                    final_color = str(found_colors)
                    multi_color = True
        # These MUST run for every single row, including Lands
        cmcs.append(cmc_val)
        colors.append(final_color)
        is_multi_colored.append(multi_color)

    df.loc[:, 'cmc'] = cmcs
    df.loc[:, 'color'] = colors
    df.loc[:, 'is_multi_colored'] = is_multi_colored
    
    return df


def enrich_land_data(df):
    """
    The 'Land Fanatic' Logic: 
    Maps the LAND_DATA_MAP to the dataframe to create boolean columns and 
    standardize land types for searching.
    """
    # Initialize all potential boolean columns based on tags in your map
    all_tags = set()
    for data in LAND_DATA_MAP.values():
        all_tags.update(data['tags'])
    
    for tag in all_tags:
        df[f'is_{tag}'] = False

    df['land_mana'] = ""

    def apply_land_logic(row):
        name = row['MatchName'].title() # LAND_DATA_MAP uses Title Case keys
        if name in LAND_DATA_MAP:
            data = LAND_DATA_MAP[name]
            row['land_mana'] = data['mana']
            for tag in data['tags']:
                row[f'is_{tag}'] = True
            
        return row

    return df.apply(apply_land_logic, axis=1)


def build_database():
    print("--- Initializing ETL ---")
    inv_path, inv_sync = get_latest_file(DATA_DIR, r"Inventory_mikelele")

    if not inv_path:
        print("❌ Critical: No Inventory file found.")
        return
    else:
        df_inventory = clean_inventory(inv_path)

    df_all_decks, decks_sync = load_all_decks_cards(DECKS_DIR)
    
    
    df_inventory = get_card_cmc_and_color(df_inventory)
    df_all_decks = get_card_cmc_and_color(df_all_decks)
    df_inventory = enrich_land_data(df_inventory)
    df_all_decks = enrich_land_data(df_all_decks)
    
    class_path = os.path.join(CLASSIFICATION_DIR, "Pauper_Playground_Decks_Classification.csv")
    df_bb_raw = pd.read_csv(class_path)
    df_bb_raw.columns = df_bb_raw.columns.str.strip()

    df_battle_box, df_all_decks = calculate_priority_buildability(df_inventory, df_all_decks, df_bb_raw)

    # Apply renames
    rename_cols(df_all_decks)
    rename_cols(df_inventory)
    rename_cols(df_battle_box)

    # Generate the Long-Form Stats Table
    # We use a combined set for overall stats or just inventory
    # df_stats_expanded = build_expanded_stats_table(df_inventory)

    conn = sqlite3.connect(DB_PATH)
    df_inventory.to_sql('inventory', conn, if_exists='replace', index=False)
    df_all_decks.to_sql('all_decks', conn, if_exists='replace', index=False)
    df_battle_box.to_sql('battle_box', conn, if_exists='replace', index=False)
    # df_stats_expanded.to_sql('stats_expanded', conn, if_exists='replace', index=False)
    
    update_date = datetime.now().strftime("%b %d, %Y")
    pd.DataFrame([{'last_update': update_date}]).to_sql('metadata', conn, if_exists='replace', index=False)
    conn.close()
    print(f"\nDB Update Complete: {update_date}")
    print(df_inventory.columns)
    print(df_all_decks.columns)

    if inv_sync or decks_sync:
        print("🚀 Changes detected in source files. Triggering GitHub Sync...")
        sync_to_github()
    else:
        print("ℹ️ No source changes detected. Repository is already up to date.")

if __name__ == "__main__":
    build_database()