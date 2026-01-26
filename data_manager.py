## data_manager.py

import sqlite3
import pandas as pd
import streamlit as st
import os

DB_PATH = os.path.join("data", "mtg_pauper.db")

@st.cache_data
def load_inventory():
    """Loads the processed inventory and the latest update timestamp."""
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT * FROM inventory", conn)
        # Grab the metadata timestamp
        meta = pd.read_sql("SELECT last_update FROM metadata", conn)
        last_update = meta['last_update'].iloc[0]
    except Exception as e:
        st.error(f"Error loading inventory: {e}")
        return pd.DataFrame(), "Unknown"
    finally:
        conn.close()
    return df, last_update

@st.cache_data
def load_all_decks():
    """Loads every card from every deck (the full card lists)."""
    conn = sqlite3.connect(DB_PATH)
    try:
        # Renamed from 'decks' to 'all_decks' to match build_db.py
        df = pd.read_sql("SELECT * FROM all_decks", conn)
    except Exception as e:
        st.error(f"Error loading card lists: {e}")
        return pd.DataFrame()
    finally:
        conn.close()
    return df

@st.cache_data
def load_battle_box():
    """Loads the gallery metadata (DeckName, Brew, Priority, Thumbnail)."""
    conn = sqlite3.connect(DB_PATH)
    try:
        # This pulls from the Google Sheets classification table we saved
        df = pd.read_sql("SELECT * FROM battle_box ORDER BY Priority ASC", conn)
    except Exception as e:
        st.error(f"Error loading Battle Box metadata: {e}")
        return pd.DataFrame()
    finally:
        conn.close()
    return df