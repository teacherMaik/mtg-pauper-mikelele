import sqlite3
import pandas as pd
import streamlit as st
import os
from maps_utilities import LAND_DATA_MAP

DB_PATH = os.path.join("data", "mtg_pauper.db")

def get_db_last_update():
    """Return the DB 'last_update' metadata string used to invalidate caches after builds."""
    conn = sqlite3.connect(DB_PATH)
    try:
        meta = pd.read_sql("SELECT last_update FROM metadata LIMIT 1", conn)
        return meta['last_update'].iloc[0] if not meta.empty else "unknown"
    except Exception as e:
        print(f"get_db_last_update error: {e}")
        return "unknown"
    finally:
        conn.close()


@st.cache_data
def load_inventory(db_last_update):
    # db_last_update used only for cache key invalidation
    _ = db_last_update

    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT * FROM inventory", conn)
    except Exception as e:
        print(f"load_inventory error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()
    return df


@st.cache_data
def load_all_decks(db_last_update):
    _ = db_last_update

    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT * FROM all_decks", conn)
        if 'rarity' in df.columns:
            df['rarity'] = df['rarity'].astype(str)
    except Exception as e:
        print(f"load_all_decks error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()
    return df


@st.cache_data
def load_battle_box(db_last_update):
    _ = db_last_update

    conn = sqlite3.connect(DB_PATH)
    try:
        df = pd.read_sql("SELECT * FROM battle_box ORDER BY Priority ASC", conn)
    except Exception as e:
        print(f"load_battle_box error: {e}")
        return pd.DataFrame()
    finally:
        conn.close()
    return df