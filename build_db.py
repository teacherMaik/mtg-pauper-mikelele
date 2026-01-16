import sqlite3
import pandas as pd
import os
from datetime import datetime

# --- CONFIGURATION ---
DB_PATH = os.path.join("data", "mtg_pauper.db")
INVENTORY_CSV = os.path.join("data", "Inventory_mikelele_2026.January.16.csv")
DECKS_PATH = os.path.join("data", "decks")

def clean_inventory(path):
    """Loads and applies Mikelele's custom cleaning logic."""
    df = pd.read_csv(path)
    
    # 1. Basic Cleaning & Column Standardization
    df['Card Number'] = pd.to_numeric(df['Card Number'], errors='coerce').fillna(0).astype(int).astype(str)
    df['Code'] = df['Edition Code'].astype(str) + "-" + df['Card Number']
    df.rename(columns={'Count': 'Qty', 'Cost': 'Mana'}, inplace=True)
    
    # 2. Price/Total Logic
    if 'Price' not in df.columns and 'My Price' in df.columns:
        df.rename(columns={'My Price': 'Price'}, inplace=True)
    
    if df['Price'].dtype == 'object':
        df['Price'] = df['Price'].str.replace('$', '', regex=False).str.replace(',', '', regex=False)
    
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0.00)
    df['Total'] = df['Price'] * df['Qty']

    # 3. Drop unneeded columns to keep DB lightweight
    to_drop = [
        'Tradelist Count', 'Decks Count Built', 'Condition', 'Language',
        'Foil', 'Signed', 'Artist Proof', 'Altered Art', 'Misprint',
        'Promo', 'Textless', 'Printing Id', 'Printing Note', 'My Price', 
        'Tags', 'Edition Code', 'Card Number', 'TcgPlayer ID', 
        'Last Updated', 'Decks Count All'
    ]
    df.drop(columns=to_drop, inplace=True, errors='ignore')
    
    return df

def load_all_decks(path):
    """Collects all deck CSVs into one master DataFrame."""
    all_deck_data = []
    if os.path.exists(path):
        for file in os.listdir(path):
            if file.endswith(".csv"):
                df = pd.read_csv(os.path.join(path, file))
                # Clean name: removal of .csv and any timestamp suffix
                clean_name = file.replace(".csv", "").split("_")[0]
                df['DeckName'] = clean_name
                all_deck_data.append(df)
    
    if all_deck_data:
        master_df = pd.concat(all_deck_data, ignore_index=True)        
        master_df.rename(columns={'Count': 'Qty', 'Cost': 'Mana'}, inplace=True)
        return master_df
    return pd.DataFrame()

def build_database():
    print("--- Starting Strictly Pauper ETL Process ---")
    
    # 1. EXTRACT
    df_inventory = clean_inventory(INVENTORY_CSV)
    df_decks = load_all_decks(DECKS_PATH)
    
    # 2. TRANSFORM: The "Exception" Logic
    # We only keep: (Rarity is Common) OR (Name is found in our decks)
    if not df_decks.empty:
        deck_card_names = df_decks['Name'].unique()
        df_inventory = df_inventory[
            (df_inventory['Rarity'] == 'Common') | 
            (df_inventory['Name'].isin(deck_card_names))
        ]
        print(f"Filter applied: Keeping Commons + {len(deck_card_names)} cards found in decks.")
    else:
        df_inventory = df_inventory[df_inventory['Rarity'] == 'Common']
        print("Warning: No deck files found. Filtering for Commons only.")

    # Extract Date from filename for the UI header
    raw_date = os.path.basename(INVENTORY_CSV).split("_")[-1].replace(".csv", "")
    try:
        date_obj = datetime.strptime(raw_date, "%Y.%B.%d")
        last_update = date_obj.strftime("%b %d, %Y")
    except:
        last_update = raw_date

    # 3. LOAD (Wipe and Replace)
    conn = sqlite3.connect(DB_PATH)
    
    # Save the filtered inventory
    df_inventory.to_sql('inventory', conn, if_exists='replace', index=False)
    
    # Save the master decks list (to allow for deck-specific views later)
    if not df_decks.empty:
        df_decks.to_sql('decks', conn, if_exists='replace', index=False)
    
    # Save metadata
    meta_df = pd.DataFrame([{'last_update': last_update}])
    meta_df.to_sql('metadata', conn, if_exists='replace', index=False)
    
    conn.close()
    
    print("--- SUCCESS ---")
    print(f"Database: {DB_PATH}")
    print(f"Final Count: {len(df_inventory)} cards stored.")

if __name__ == "__main__":
    build_database()