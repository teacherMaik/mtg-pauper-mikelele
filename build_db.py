import sqlite3
import pandas as pd
import os
import re
from datetime import datetime
from maps_utilities import LAND_DATA_MAP
from maps_decks import DECKS_MAP
from sync_git import sync_to_github

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
    # Delete Older Versions and set sync_github true to remove from remote repo
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

    df['Edition Code'] = df['Edition Code'].fillna('').astype(str).str.strip().str.upper()

    df['Card Number'] = pd.to_numeric(df['Card Number'], errors='coerce').fillna(0).astype(int).astype(str)
    df['Code'] = df['Edition Code'] + " - " + df['Card Number']

    df['Price'] = df['Price'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0.00)
    df['Count'] = pd.to_numeric(df['Count'], errors='coerce').fillna(0).astype(int)
    df['Total'] = df['Count'] * df['Price']
    df['MatchName'] = df['Name'].apply(get_match_name)

    drop_cols = ['Tradelist Count', 'Decks Count Built', 'Decks Count All', 'Condition', 'Language', 'Foil', 'Signed', 'Artist Proof', 'Altered Art', 'Misprint', 'Promo', 'Textless', 'Printing Id','Printing Note', 'Tags', 'My Price', 'Last Updated', 'TcgPlayer ID', 'Edition Code', 'Card Number']
    df.drop(columns=drop_cols, inplace=True, errors='ignore')

    print("printing null codes:", df['Code'].isna().sum())
    print(df.loc[df['Code'].isna(), 'Name'])

    return df


def load_all_decks_cards(path, df_inventory):
    if not os.path.exists(path): return pd.DataFrame(), False

    all_deck_data = []
    files = [f for f in os.listdir(path) if f.endswith(".csv")]
    if not files: return pd.DataFrame(), False

    ## ADAPT PREFIX AS NEEDED FOR CSV FILES
    prefixes = set(re.split(r'_mikelele', f)[0] for f in files)
    any_new_deck = False

    inv_ref = df_inventory.drop_duplicates('Code').set_index('Code')[
        ['Edition', 'Image URL', 'Scryfall ID', 'Price', 'Rarity']
    ].to_dict('index')

    missing_inv = 0
    for prefix in prefixes:
        deck_name = prefix.strip()
        latest_deck, status = get_latest_file(path, rf"^{re.escape(prefix)}_mikelele")
        if status: any_new_deck = True

        if latest_deck:
            df = pd.read_csv(latest_deck)
            deck_rules = DECKS_MAP.get(deck_name, {}).get("cards", {})
            
            df['DeckName'] = prefix.strip()
            
            # Standardize Price/Count immediately so math works for EVERY row
            df['Price'] = df['Price'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0.00)
            df['Count'] = pd.to_numeric(df.get('Count', df.get('Qty', 0)), errors='coerce').fillna(0).astype(int)
            df['Section'] = df.get('Section', df.get('section', 'Main')) # Safety for the KeyError
    
            df['MatchName'] = df['Name'].apply(get_match_name)
            df.drop(['Last Updated', 'TcgPlayer ID'], axis=1, inplace=True, errors='ignore')

            purified_rows = []
            for _, row in df.iterrows():
                cardeck_name = row['Name']

                if cardeck_name in deck_rules:
                    # Logic for Mapped cards
                    entries = deck_rules[cardeck_name]
                    for entry in entries:
                        # Only process entries matching current CSV section
                        if entry['section'].lower() != row['Section'].lower():
                            continue
                            
                        new_row = row.copy()
                        new_row['Count'] = entry['qty']
                        new_row['Code'] = entry['code']
                        new_row['Section'] = entry['section']
                        new_row['Edition'] = entry['edition']
                        
                        info = inv_ref.get(entry['code'], {})

                        if info:
                            new_row['Price'] = info.get('Price', row['Price'])
                            new_row['Rarity'] = info.get('Rarity', row['Rarity'])
                            new_row['Image URL'] = info.get('Image URL', row['Image URL'])
                            new_row['Scryfall ID'] = info.get('Scryfall ID', row['Scryfall ID'])
                        else:
                            missing_inv += 1

                        new_row['Total'] = new_row['Count'] * new_row['Price']
                        purified_rows.append(new_row)
                else:
                    # CRITICAL FIX: Append the original row if not in map
                    # This prevents the empty DataFrame that causes the KeyError
                    row['Code'] = 'UNKNOWN'
                    row['Total'] = row['Count'] * row['Price']
                    purified_rows.append(row)

            all_deck_data.append(pd.DataFrame(purified_rows))

    final_df = pd.concat(all_deck_data, ignore_index=True) if all_deck_data else pd.DataFrame()
    return final_df, any_new_deck


def enrich_buildability_deck_colors(df_inventory, df_all_decks, df_bb):
    # Map physical inventory by Code
    virtual_inv = df_inventory.groupby('Code')['Count'].sum().to_dict()
    
    # Add the 'is_main' flag and priority for sorting. Copies go to Main Decks before Sideboards
    df_cards = df_all_decks.copy()
    df_cards['is_main'] = df_cards['Section'].str.lower().str.contains('main', na=False)
    
    # Merge deck priority from df_bb (the dashboard map)
    df_cards = df_cards.merge(df_bb[['DeckName', 'Priority']], on='DeckName', how='left')

    # 3. GLOBAL SORT: All Mains (True=1) first, then by deck priority
    df_cards = df_cards.sort_values(
        by=['is_main', 'Priority', 'DeckName'], 
        ascending=[False, True, True]
    )

    # We will store color counts, then merge them into df_bb at the end
    color_stats = {} 
    valid_colors = ['W', 'U', 'B', 'R', 'G', 'C', 'L']

    #  Allocation
    allocations = []

    for idx, card in df_cards.iterrows():
        
        code = card['Code']
        needed = card['Count']
        available = virtual_inv.get(code, 0)
        
        taken = min(needed, available)
        allocations.append({
            'temp_idx': idx,
            'NumForBuild': taken,
            'Priority': card['Priority']
        })
        virtual_inv[code] = available - taken

        deck_name = card['DeckName']
        if deck_name not in color_stats:
            color_stats[deck_name] = {f"{s}_{c}": 0 for s in ['main', 'side'] for c in valid_colors}
            color_stats[deck_name]['main_card_count'] = 0
            color_stats[deck_name]['side_card_count'] = 0

        # Determine if we are updating main or side columns
        prefix = 'main' if card['is_main'] else 'side'
        color_stats[deck_name][f'{prefix}_card_count'] += needed
        
        # Check the card's color string (e.g., 'RG') and increment appropriate columns
        card_color_str = str(card.get('color', ''))
        for c in valid_colors:
            if c in card_color_str:
                color_stats[deck_name][f'{prefix}_{c}'] += needed

    # Map results back to the original index to preserve order
    df_allocs = pd.DataFrame(allocations).set_index('temp_idx')
    df_all_decks['NumForBuild'] = df_allocs['NumForBuild'].fillna(0).astype(int)
    df_all_decks['Priority'] = df_allocs['Priority'].fillna(9999).astype(int)
    df_all_decks['need_buy'] = (
        (df_all_decks['Count'] - df_all_decks['NumForBuild'])
        .clip(lower=0)
        .fillna(0)
        .astype(int)
    )

    df_color_summary = pd.DataFrame.from_dict(color_stats, orient='index').reset_index()
    df_color_summary.rename(columns={'index': 'DeckName'}, inplace=True)
    
    # Remove old columns if they exist before merging to avoid .x .y duplicates
    cols_to_drop = [c for c in df_color_summary.columns if c in df_bb.columns and c != 'DeckName']
    df_bb = df_bb.drop(columns=cols_to_drop).merge(df_color_summary, on='DeckName', how='left')

    # Calculate Pcts for the Dashboard (df_bb)
    main_pcts, side_pcts = [], []
    for _, deck in df_bb.iterrows():
        deck_name = deck['DeckName']
        d_cards = df_all_decks[df_all_decks['DeckName'] == deck_name]
        
        def get_section_pct(main_flag):
            section = d_cards[d_cards['Section'].str.lower().str.contains('main', na=False) == main_flag]
            total = section['Count'].sum()
            if total == 0: return 100
            return int((section['NumForBuild'].sum() / total) * 100)

        main_pcts.append(get_section_pct(True))
        side_pcts.append(get_section_pct(False))

    df_bb['CompletionPct'] = main_pcts
    df_bb['SideboardPct'] = side_pcts


    return df_bb, df_all_decks


def get_card_cmc_color_primary_type(df):
    pattern = r'\{(.*?)\}'
    color_map = {'W':'W', 'U':'U', 'B':'B', 'R':'R', 'G':'G'}
    cmcs, cmcs_with_x, colors, is_multi_colored, primary_types_for_deck = [], [], [], [], []

    df = df.copy()

    for _, row in df.iterrows():
        mana_str = str(row.get('Cost', '')).strip()
        type_line = str(row.get('Type', ''))
        
        # Default values for Lands
        if "Land" in type_line:
            cmc_val = 0
            cmc_has_x = False
            final_color = "L" # 'L' keeps them out of the 'C' (Colorless) slice
            multi_color = False
            primary_type = 'Land'

        else:
            # CMC Calculation
            parts = mana_str.split('//')
            parts_cmc = []
            cmc_has_x = False

            for p in parts:

                symbols = re.findall(pattern, p)

                if any(s.upper() == 'X' for s in symbols):
                    cmc_has_x = True
                
                val = sum(int(s) if s.isdigit() else (0 if s.upper() == 'X' else 1) for s in symbols if s)
                parts_cmc.append(val)

            cmc_val = parts_cmc[0] if parts_cmc else 0
            
            # Color Classification
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

            # Primary Type For Decks
            front_face = type_line.split('//')[0].strip()
            # Priority order is key
            if "Creature" in front_face: 
                primary_type = "Creature"
            elif "Instant" in front_face: 
                primary_type = "Instant"
            elif "Sorcery" in front_face: 
                primary_type = "Sorcery"
            elif "Enchantment" in front_face: 
                primary_type = "Enchantment"
            elif "Artifact" in front_face: 
                primary_type = "Artifact"
            
        # These MUST run for every single row, including Lands
        cmcs.append(cmc_val)
        cmcs_with_x.append(cmc_has_x)
        colors.append(final_color)
        is_multi_colored.append(multi_color)
        primary_types_for_deck.append(primary_type)

    return df.assign(
        cmc=cmcs,
        cmc_has_x=cmcs_with_x,
        color=colors,
        is_multi_colored=is_multi_colored,
        primary_type_for_deck=primary_types_for_deck
    )


def enrich_land_data(df):
    
    NORMALIZED_MAP = {k.lower().strip(): v for k, v in LAND_DATA_MAP.items()}
    # Initialize all potential boolean columns based on tags in your map
    all_tags = set()
    for data in NORMALIZED_MAP.values():
        all_tags.update(data['tags'])
    
    for tag in all_tags:
        df[f'is_{tag}'] = False

    df['land_mana'] = ""

    def apply_land_logic(row):
        name = row['MatchName']
        if name in NORMALIZED_MAP:
            data = NORMALIZED_MAP[name]
            row['land_mana'] = data['mana']
            for tag in data['tags']:
                row[f'is_{tag}'] = True
            
        return row

    return df.apply(apply_land_logic, axis=1)


def build_database():
    
    inv_path, inv_sync = get_latest_file(DATA_DIR, r"Inventory_mikelele")

    if not inv_path:
        print("❌ Critical: No Inventory file found.")
        return
    else:
        df_inventory = clean_inventory(inv_path)

    df_inventory = get_card_cmc_color_primary_type(df_inventory)
    df_inventory = enrich_land_data(df_inventory)

    df_all_decks, decks_sync = load_all_decks_cards(DECKS_DIR, df_inventory)
    df_all_decks = get_card_cmc_color_primary_type(df_all_decks)
    df_all_decks = enrich_land_data(df_all_decks)
    
    class_path = os.path.join(CLASSIFICATION_DIR, "Pauper_Playground_Decks_Classification.csv")
    df_bb_raw = pd.read_csv(class_path)
    df_bb_raw.columns = df_bb_raw.columns.str.strip()

    df_battle_box, df_all_decks = enrich_buildability_deck_colors(df_inventory, df_all_decks, df_bb_raw)

    # Apply renames
    rename_cols(df_all_decks)
    rename_cols(df_inventory)
    rename_cols(df_battle_box)

    print(df_inventory.columns)
    print(df_all_decks.columns)

    # Rebuild DB on each run
    conn = sqlite3.connect(DB_PATH)
    df_inventory.to_sql('inventory', conn, if_exists='replace', index=False)
    df_all_decks.to_sql('all_decks', conn, if_exists='replace', index=False)
    df_battle_box.to_sql('battle_box', conn, if_exists='replace', index=False)
    
    update_date = datetime.now().strftime("%b %d, %Y")
    pd.DataFrame([{'last_update': update_date}]).to_sql('metadata', conn, if_exists='replace', index=False)
    conn.close()
    print(f"\nDB Update Complete: {update_date}")
    
    # Sync Github repo if new files were detected
    if inv_sync or decks_sync:
        print("🚀 Changes detected in source files. Triggering GitHub Sync...")
        sync_to_github()
    else:
        print("ℹ️ No source changes detected. Repository is already up to date.")

if __name__ == "__main__":
    build_database()