import sqlite3
import pandas as pd
import os
import re
from datetime import datetime

# --- CONFIGURATION ---
DB_PATH = os.path.join("data", "mtg_pauper.db")
DATA_DIR = "data"
DECKS_DIR = os.path.join("data", "decks")

def get_latest_file(directory, pattern):
    """
    Finds files matching a pattern, sorts them by date in filename, 
    returns the latest and deletes the others.
    """
    files = [f for f in os.listdir(directory) if re.search(pattern, f) and f.endswith(".csv")]
    if not files:
        return None

    # Helper to extract date from your format: Name_YYYY.Month.DD.csv
    def extract_date(filename):
        match = re.search(r"(\d{4})\.(\w+)\.(\d{1,2})", filename)
        if match:
            try:
                return datetime.strptime(f"{match.group(1)} {match.group(2)} {match.group(3)}", "%Y %B %d")
            except:
                return datetime.min
        return datetime.min

    # Sort files by the parsed date
    files.sort(key=extract_date, reverse=True)
    
    latest_file = os.path.join(directory, files[0])
    
    # Delete the older versions
    for old_file in files[1:]:
        old_path = os.path.join(directory, old_file)
        print(f"🗑️ Deleting old version: {old_file}")
        os.remove(old_path)
        
    return latest_file

def clean_inventory(path):
    df = pd.read_csv(path)
    df['Card Number'] = pd.to_numeric(df['Card Number'], errors='coerce').fillna(0).astype(int).astype(str)
    df['Code'] = df['Edition Code'].astype(str) + "-" + df['Card Number']
    df.rename(columns={'Count': 'Qty', 'Cost': 'Mana'}, inplace=True)
    
    if 'Price' not in df.columns and 'My Price' in df.columns:
        df.rename(columns={'My Price': 'Price'}, inplace=True)
    
    if df['Price'].dtype == 'object':
        df['Price'] = df['Price'].str.replace('$', '', regex=False).str.replace(',', '', regex=False)
    
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0.00)
    df['Total'] = df['Price'] * df['Qty']

    to_drop = ['Tradelist Count', 'Decks Count Built', 'Condition', 'Language',
               'Foil', 'Signed', 'Artist Proof', 'Altered Art', 'Misprint',
               'Promo', 'Textless', 'Printing Id', 'Printing Note','My Price', 'Tags', 
               'Edition Code', 'Card Number', 'TcgPlayer ID', 'Last Updated', 'Decks Count All']
    df.drop(columns=to_drop, inplace=True, errors='ignore')
    return df

def load_all_decks(path):
    all_deck_data = []
    if os.path.exists(path):
        # Change: split by '_mikelele' to get the full deck name
        # This keeps "Mono B Devotion" separate from "Mono B Sacrifice"
        files = [f for f in os.listdir(path) if f.endswith(".csv")]
        
        # Identify unique deck prefixes (e.g., "Mono B Devotion")
        # Using a regex to catch everything before the first underscore followed by 'mikelele'
        prefixes = set(re.split(r'_mikelele', f)[0] for f in files)
        
        for prefix in prefixes:
            # Get the latest version for this specific deck name
            latest_deck = get_latest_file(path, rf"^{re.escape(prefix)}_mikelele")
            if latest_deck:
                df = pd.read_csv(latest_deck)
                df['DeckName'] = prefix
                all_deck_data.append(df)
    
    if all_deck_data:
        master_df = pd.concat(all_deck_data, ignore_index=True)        
        master_df.rename(columns={'Count': 'Qty', 'Cost': 'Mana'}, inplace=True)
        if df['Price'].dtype == 'object':
            df['Price'] = df['Price'].str.replace('$', '', regex=False).str.replace(',', '', regex=False)
        
        df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0.00)
        df.drop(columns=['TcgPlayer ID'], inplace=True, errors='ignore')
        return master_df
    return pd.DataFrame()

def build_database():
    print("--- Starting Version-Controlled ETL ---")
    
    # 1. FIND LATEST & CLEANUP
    inventory_path = get_latest_file(DATA_DIR, r"Inventory_mikelele")
    if not inventory_path:
        print("❌ Error: No Inventory CSV found.")
        return

    df_inventory = clean_inventory(inventory_path)
    df_decks = load_all_decks(DECKS_DIR)
    
    # 2. TRANSFORM (Strictly Pauper Filter)
    if not df_decks.empty:
        deck_card_names = df_decks['Name'].unique()
        df_inventory = df_inventory[
            (df_inventory['Rarity'] == 'Common') | 
            (df_inventory['Name'].isin(deck_card_names))
        ]

    # 3. LOAD
    conn = sqlite3.connect(DB_PATH)
    df_inventory.to_sql('inventory', conn, if_exists='replace', index=False)
    if not df_decks.empty:
        df_decks.to_sql('decks', conn, if_exists='replace', index=False)
    
    # Save Metadata
    update_date = datetime.now().strftime("%b %d, %Y")
    pd.DataFrame([{'last_update': update_date}]).to_sql('metadata', conn, if_exists='replace', index=False)
    
    conn.close()
    print(f"--- SUCCESS: DB built with {len(df_inventory)} cards. ---")

if __name__ == "__main__":
    build_database()