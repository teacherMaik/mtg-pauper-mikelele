import re
import pandas as pd
import streamlit as st

@st.cache_data
def get_stats(df):
    if df is None or df.empty:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # 1. Color Stats (WUBRG + C)
    # We map the UI names and check the 'color' column for presence
    color_map = {'White': 'W', 'Blue': 'U', 'Black': 'B', 'Red': 'R', 'Green': 'G', 'Colorless': 'C'}
    color_rows = []
    
    for label, code in color_map.items():
        # Check if the code exists in the string (handles 'WB', 'WUR', etc.)
        mask = df['color'].str.contains(code, na=False)
        subset = df[mask]
        if not subset.empty:
            color_rows.append({
                'Color': label,
                'Count': subset['qty'].sum(),
                'Value': subset['total_cards_value'].sum()
            })
    df_color = pd.DataFrame(color_rows)

    # 2. Type Stats (Same logic as before)
    valid_types = ['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment', 'Planeswalker', 'Land', 'Battle']
    type_rows = []
    for t in valid_types:
        mask = df['type'].str.contains(t, na=False, case=False)
        subset = df[mask]
        if not subset.empty:
            type_rows.append({
                'Type': t,
                'Count': subset['qty'].sum(),
                'Value': subset['total_cards_value'].sum()
            })
    df_type = pd.DataFrame(type_rows).sort_values(by='Count', ascending=True)

    # 3. CMC Stats (Using your fixed integer 'cmc' column)
    df_non_land = df[~df['type'].str.contains('Land', na=False, case=False)]
    df_cmc = df_non_land.groupby('cmc').agg(Count=('qty', 'sum'), Value=('total_cards_value', 'sum')).reset_index()
    df_cmc.rename(columns={'cmc': 'CMC'}, inplace=True)

    return df_color, df_type, df_cmc

@st.cache_data
def get_land_breakdown(df):
    cat = {'Basic':0, 'Snow':0, 'Dual Basics':0, 'Snow Duals':0, 'Artifact Lands':0, 'Others':0}
    vals = {'Basic':0.0, 'Snow':0.0, 'Dual Basics':0.0, 'Snow Duals':0.0, 'Artifact Lands':0.0, 'Others':0.0}
    basic_types = ['Plains', 'Island', 'Swamp', 'Mountain', 'Forest']
    
    # Ensure columns are lowercase for consistent filtering
    df_c = df.copy()
    df_c.columns = [c.lower() for c in df_c.columns]
    
    # Filter for lands
    lands = df_c[df_c['type'].str.contains('Land', na=False, case=False)]
    
    for _, row in lands.iterrows():
        t, n = str(row.get('type', '')), str(row.get('name', ''))
        q = int(row.get('qty', 1))
        v = float(row.get('total_cards_value', 0.0))
        
        is_snow = "Snow" in t or "Snow" in n
        type_count = sum(1 for bt in basic_types if bt in t)
        is_dual = type_count >= 2
        
        if "Artifact" in t: k = 'Artifact Lands'
        elif is_snow and is_dual: k = 'Snow Duals'
        elif is_dual: k = 'Dual Basics'
        elif is_snow: k = 'Snow'
        elif "Basic" in t or any(bt == t.strip() for bt in basic_types): k = 'Basic'
        else: k = 'Others'
        
        cat[k] += q
        vals[k] += v
        
    return pd.DataFrame([{'Stat': k, 'Count': cat[k], 'Value': vals[k]} for k in cat.keys()])

@st.cache_data
def get_set_stats(df):
    return df.groupby('edition').agg(qty=('qty', 'sum'), total_cards_value=('total_cards_value', 'sum')).reset_index()

@st.cache_data
def get_rarity_stats(df):
    return df.groupby('rarity').agg(qty=('qty', 'sum'), total_cards_value=('total_cards_value', 'sum')).reset_index()