import sqlite3
import pandas as pd
import streamlit as st
import os
from utility_maps import LAND_DATA_MAP

DB_PATH = os.path.join("data", "mtg_pauper.db")

@st.cache_data
def load_inventory():
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT * FROM inventory", conn)
        meta = pd.read_sql("SELECT last_update FROM metadata", conn)
        last_update = meta['last_update'].iloc[0] if not meta.empty else "Unknown"
    except Exception as e:
        return pd.DataFrame(), "Unknown"
    finally:
        conn.close()
    return df, last_update

@st.cache_data
def load_all_decks():
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT * FROM all_decks", conn)
    except:
        return pd.DataFrame()
    finally:
        conn.close()
    return df

@st.cache_data
def load_battle_box():
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT * FROM battle_box ORDER BY Priority ASC", conn)
    except:
        return pd.DataFrame()
    finally:
        conn.close()
    return df

@st.cache_data
def load_stats_expanded():
    """Specifically for the analytics charts."""
    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT * FROM stats_expanded", conn)
    except:
        return pd.DataFrame()
    finally:
        conn.close()
    return df


def find_unmapped_lands():
    conn = sqlite3.connect("data/mtg_pauper.db")
    # Fetch all cards with "Land" in the type line
    df = pd.read_sql("SELECT name FROM inventory WHERE type LIKE '%Land%'", conn)
    conn.close()

    # Get unique names from inventory
    inv_lands = set(df['name'].unique())
    # Get unique names from your map (ensuring case consistency)
    mapped_lands = set(LAND_DATA_MAP.keys())

    missing = [l for l in inv_lands if l not in mapped_lands]
    
    print(f"🔍 Found {len(missing)} unmapped lands:")
    for land in sorted(missing):
        print(f"  - {land}")

if __name__ == "__main__":
    find_unmapped_lands()