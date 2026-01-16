import sqlite3
import pandas as pd
import streamlit as st

DB_PATH = 'data/mtg_pauper.db'

@st.cache_data
def load_inventory():
    conn = sqlite3.connect(DB_PATH)
    # Since build_db.py already filtered the 'inventory' table, 
    # we can just grab everything.
    df = pd.read_sql("SELECT * FROM inventory", conn)
    
    # Grab the metadata timestamp
    meta = pd.read_sql("SELECT last_update FROM metadata", conn)
    last_update = meta['last_update'].iloc[0]
    
    conn.close()
    return df, last_update

@st.cache_data
def load_all_decks():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM decks", conn)
    conn.close()
    return df