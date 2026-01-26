import sqlite3
import pandas as pd
import os
import re
from datetime import datetime

# --- CONFIGURATION ---
DB_PATH = os.path.join("data", "mtg_pauper.db")
DATA_DIR = "data"
CLASSIFICATION_DIR = "data" 
DECKS_DIR = os.path.join("data", "decks")

def get_match_name(name):
    """Aggressively cleans card names for matching across sources."""
    if not isinstance(name, str): return ""
    # Remove content in parens/brackets and lowercase
    name = re.sub(r'\(.*?\)|\[.*?\]', '', name)
    return name.lower().strip()

def get_latest_file(directory, pattern):
    files = [f for f in os.listdir(directory) if re.search(pattern, f) and f.endswith(".csv")]
    if not files: return None
    def extract_date(filename):
        match = re.search(r"(\d{4})\.(\w+)\.(\d{1,2})", filename)
        if match:
            try: return datetime.strptime(f"{match.group(1)} {match.group(2)} {match.group(3)}", "%Y %B %d")
            except: return datetime.min
        return datetime.min
    files.sort(key=extract_date, reverse=True)
    return os.path.join(directory, files[0])

def clean_inventory(path):
    df = pd.read_csv(path)

    # Strip whitespace and fill empty values to avoid 'nan' strings
    df['Edition Code'] = df['Edition Code'].astype(str).str.strip().fillna('')
    df['Card Number'] = df['Card Number'].astype(str).str.strip().fillna('')
    df['Code'] = df['Edition Code'] + " - " + df['Card Number']
    
    # Convert Price to string first to use .str.replace, then to numeric
    df['Price'] = (
        df['Price']
        .astype(str)
        .str.replace('$', '', regex=False)
        .str.replace(',', '', regex=False)
    )
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0.00)

    # 3. Calculate Total (Using 'Count' before it gets renamed to 'Qty')
    # We ensure Count is numeric just in case
    df['Count'] = pd.to_numeric(df['Count'], errors='coerce').fillna(0).astype(int)
    df['Total'] = df['Count'] * df['Price']

    # 4. Standardize Remaining Columns
    df.rename(columns={'Count': 'Qty', 'Cost': 'Mana'}, inplace=True, errors='ignore')

    df.drop(columns=
            ['Tradelist Count', 'Decks Count Built', 'Decks Count All',
             'Edition Code', 'Card Number','Condition', 'Language', 'Foil',
             'Signed', 'Artist Proof', 'Altered Art', 'Misprint', 'Promo',
             'Textless', 'Printing Id','Printing Note', 'Tags', 'My Price',
             'Last Updated', 'TcgPlayer Id'], inplace=True, errors='ignore')
    

    # Appends cleaned name card names col for matching against decks for availability
    df['MatchName'] = df['Name'].apply(get_match_name)

    df.rename(columns={'Count': 'Qty', 'Cost': 'Mana'}, inplace=True, errors='ignore')

    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0.00)
    return df

def load_all_decks_cards(path):
    all_deck_data = []
    if not os.path.exists(path): return pd.DataFrame()
    files = [f for f in os.listdir(path) if f.endswith(".csv")]
    prefixes = set(re.split(r'_mikelele', f)[0] for f in files)
    
    for prefix in prefixes:
        latest_deck = get_latest_file(path, rf"^{re.escape(prefix)}_mikelele")
        if latest_deck:
            df = pd.read_csv(latest_deck)
            df['DeckName'] = prefix.strip()

            # Convert Price to string first to use .str.replace, then to numeric
            df['Price'] = (
                df['Price']
                .astype(str)
                .str.replace('$', '', regex=False)
                .str.replace(',', '', regex=False)
            )
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0.00)

            # Clean Count & Calculate Total
            # Standardize 'Count' or 'Qty' column name early to avoid errors
            if 'Count' in df.columns:
                df.rename(columns={'Count': 'Qty'}, inplace=True)
            
            df['Qty'] = pd.to_numeric(df['Qty'], errors='coerce').fillna(0).astype(int)
            df['Total'] = df['Qty'] * df['Price']
            
            # 3. Final Standardizations
            df.rename(columns={'Cost': 'Mana'}, inplace=True, errors='ignore')
            df['MatchName'] = df['Name'].apply(get_match_name)
            
            # Flexible Section column
            if 'Section' not in df.columns and 'Board' in df.columns:
                df.rename(columns={'Board': 'Section'}, inplace=True)
            
            all_deck_data.append(df)
    return pd.concat(all_deck_data, ignore_index=True) if all_deck_data else pd.DataFrame()

def calculate_priority_buildability(df_inventory, df_all_decks, df_battle_box):
    virtual_inv = df_inventory.groupby('MatchName')['Qty'].sum().to_dict()
    
    df_bb = df_battle_box.copy()
    df_bb['DeckName'] = df_bb['DeckName'].str.strip()
    df_bb = df_bb.sort_values('Priority')
    
    completion_rates = []

    print("\n" + "="*50)
    print("      BATTLE BOX BUILDABILITY AUDIT")
    print("="*50)

    for _, row in df_bb.iterrows():
        deck_name = row['DeckName']
        
        # Filter for Deck + Section containing 'Main' (handles Main, Mainboard, etc)
        deck_cards = df_all_decks[
            (df_all_decks['DeckName'] == deck_name) & 
            (df_all_decks['Section'].str.contains('Main', case=False, na=False))
        ]
        
        total_needed = deck_cards['Qty'].sum()
        
        if total_needed == 0:
            found_sections = df_all_decks[df_all_decks['DeckName'] == deck_name]['Section'].unique()
            print(f"❌ {deck_name.upper()}: No 'Main' cards found! (Sections found: {list(found_sections)})")
            completion_rates.append(0)
            continue
            
        acquired = 0
        missing_report = []

        for _, card in deck_cards.iterrows():
            m_name = card['MatchName']
            real_name = card['Name']
            needed = card['Qty']
            available = virtual_inv.get(m_name, 0)
            
            taken = min(needed, available)
            acquired += taken
            
            # If we didn't get enough, log what's missing
            if taken < needed:
                missing_report.append(f"   - {needed - taken}x {real_name}")
            
            # Subtract from virtual pool
            virtual_inv[m_name] = available - taken
            
        calc_pct = int((acquired / total_needed) * 100)
        completion_rates.append(calc_pct)
        
        status_icon = "✅" if calc_pct == 100 else "⚠️"
        print(f"{status_icon} {deck_name}: {calc_pct}% ({acquired}/{total_needed})")
        
        if missing_report:
            print("\n".join(missing_report))
            print("-" * 30)

    df_bb['CompletionPct'] = completion_rates
    return df_bb

def build_database():
    print("--- Initializing ETL ---")
    inv_path = get_latest_file(DATA_DIR, r"Inventory_mikelele")
    df_inventory = clean_inventory(inv_path)
    df_all_decks = load_all_decks_cards(DECKS_DIR)
    
    class_path = os.path.join(CLASSIFICATION_DIR, "Pauper_Playground_Decks_Classification.csv")
    df_bb_raw = pd.read_csv(class_path)
    df_bb_raw.columns = df_bb_raw.columns.str.strip()

    df_battle_box = calculate_priority_buildability(df_inventory, df_all_decks, df_bb_raw)

    conn = sqlite3.connect(DB_PATH)
    df_inventory.to_sql('inventory', conn, if_exists='replace', index=False)
    df_all_decks.to_sql('all_decks', conn, if_exists='replace', index=False)
    df_battle_box.to_sql('battle_box', conn, if_exists='replace', index=False)
    
    update_date = datetime.now().strftime("%b %d, %Y")
    pd.DataFrame([{'last_update': update_date}]).to_sql('metadata', conn, if_exists='replace', index=False)
    conn.close()
    print(f"\nDB Update Complete: {update_date}")

if __name__ == "__main__":
    build_database()