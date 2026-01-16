import streamlit as st
import pandas as pd
from datetime import datetime
import os

@st.cache_data
def load_inventory():
    filename = "Inventory_mikelele_2026.January.15.csv" # Your file name
    path = os.path.join("data", filename)
    df = pd.read_csv(path)

    raw_date = filename.split("_")[-1].replace(".csv", "")
    # raw_date is "2026.January.15"
    try:
        date_obj = datetime.strptime(raw_date, "%Y.%B.%d")
        last_update = date_obj.strftime("%b %d, %Y") # Result: Jan 15, 2026
    except:
        last_update = raw_date # Fallback
    
    # Cleaning Logic
    df['Card Number'] = pd.to_numeric(df['Card Number'], errors='coerce').fillna(0).astype(int).astype(str)
    df['Code'] = df['Edition Code'].astype(str) + "-" + df['Card Number']
    df.rename(columns={'Count': 'Qty', 'Cost': 'Mana'}, inplace=True)
    
    if 'Price' not in df.columns and 'My Price' in df.columns:
        df.rename(columns={'My Price': 'Price'}, inplace=True)
    
    if df['Price'].dtype == 'object':
        df['Price'] = df['Price'].str.replace('$', '', regex=False).str.replace(',', '', regex=False)
    
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0.00)

    to_drop = ['Tradelist Count', 'Decks Count Built', 'Condition', 'Language',
               'Foil', 'Signed', 'Artist Proof', 'Altered Art', 'Misprint',
               'Promo', 'Textless', 'Printing Id', 'Printing Note','My Price', 'Tags', 
               'Edition Code', 'Card Number', 'TcgPlayer ID', 'Last Updated', 'Decks Count All']
    df.drop(columns=to_drop, inplace=True, errors='ignore')

    # Append the Total Column
    # Calculation: Price * Inventory
    df['Total'] = df['Price'] * df['Qty']

    print("--- INVENTORY HEAD ---")
    print(df.head())
    return df, last_update

@st.cache_data
def load_all_decks():
    deck_path = os.path.join("data", "decks")
    all_deck_data = []
    
    if os.path.exists(deck_path):
        for file in os.listdir(deck_path):
            if file.endswith(".csv"):
                df = pd.read_csv(os.path.join(deck_path, file))
                clean_name = file.replace(".csv", "").split("_")[0]
                df['DeckName'] = clean_name
                all_deck_data.append(df)
    
    if all_deck_data:
        master_df = pd.concat(all_deck_data, ignore_index=True)        
        master_df.rename(columns={'Count': 'Qty', 'Cost': 'Mana'}, inplace=True)
        master_df.drop(columns=['TcgPlayer ID', 'Last Updated'], inplace=True, errors='ignore')
        return master_df
    return pd.DataFrame()