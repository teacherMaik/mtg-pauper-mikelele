import sqlite3
import pandas as pd
import os
import re
from datetime import datetime

# --- CONFIGURATION ---
DB_PATH = os.path.join("data", "mtg_pauper.db")
INVENTORY_CSV = os.path.join("data", "Inventory_mikelele_2026.January.15.csv")
DECKS_PATH = os.path.join("data", "decks")

def clean_inventory(path):
    """Loads and applies Mikelele's custom cleaning logic."""
    df = pd.read_csv(path)
    
    # 1. Basic Cleaning
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
    to_drop = ['Tradelist Count', 'Decks Count Built', 'Condition', 'Language',
               'Foil', 'Signed', 'Artist Proof', 'Altered Art', 'Misprint',
               'Promo', 'Textless', 'Printing Id', 'Printing Note','My Price', 'Tags', 
               'Edition Code', 'Card Number', 'TcgPlayer ID', 'Last Updated', 'Decks Count All']
    df.drop(columns=to_drop, inplace=True, errors='ignore')
    
    return df

def load_all_decks(path):
    """Collects all deck CSVs into one master DataFrame."""
    all_deck_data = []
    if os.path.exists(path):
        for file in os.listdir(path):
            if file.endswith(".csv"):
                df = pd.read_csv(os.path.join(path, file))
                clean_name = file.replace(".csv", "").split("_")[0]
                df['DeckName'] = clean_name
                all_deck_data.append(df)
    
    if all_deck_data:
        master_df = pd.concat(all_deck_data, ignore_index=True)        
        master_df.rename(columns={'Count': 'Qty', 'Cost': 'Mana'}, inplace=True)
        return master_df
    return pd.DataFrame()

def build_database():
    print("--- Starting ETL Process ---")
    
    # 1. EXTRACT & TRANSFORM
    df_inventory = clean_inventory(INVENTORY_CSV)
    df_decks = load_all_decks(DECKS_PATH)
    
    # Extract Date from filename
    raw_date = os.path.basename(INVENTORY_CSV).split("_")[-1].replace(".csv", "")
    try:
        date_obj = datetime.strptime(raw_date, "%Y.%B.%d")
        last_update = date_obj.strftime("%b %d, %Y")
    except:
        last_update = raw_date

    # 2. LOAD (Wipe and Replace)
    conn = sqlite3.connect(DB_PATH)
    
    # Save the full inventory
    df_inventory.to_sql('inventory', conn, if_exists='replace', index=False)
    print(f"Stored {len(df_inventory)} cards in 'inventory' table.")
    
    # Save the master decks list
    if not df_decks.empty:
        df_decks.to_sql('decks', conn, if_exists='replace', index=False)
        print(f"Stored {len(df_decks)} deck entries in 'decks' table.")
    
    # Save metadata
    meta_df = pd.DataFrame([{'last_update': last_update}])
    meta_df.to_sql('metadata', conn, if_exists='replace', index=False)
    
    conn.close()
    print(f"--- SUCCESS: DB built at {DB_PATH} ---")
    print(f"Timestamp: {last_update}")

if __name__ == "__main__":
    build_database()