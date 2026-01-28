import sqlite3
import pandas as pd
import streamlit as st
import os

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