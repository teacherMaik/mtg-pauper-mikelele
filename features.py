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


@st.cache_data
def get_battle_box_stats(df_battle_box, df_all_decks, section):
    categories = ["Meta", "Brew", "Aggro", "Midrange", "Tempo", "Control"]
    stats_list = []

    # Helper for card stats - Fixed Syntax
    def calc_card_stats(deck_names):
        # Correct multi-condition filtering
        mask = (df_all_decks['DeckName'].isin(deck_names)) & \
               (df_all_decks['section'].str.contains(section, case=False, na=False))
        subset = df_all_decks[mask]
        
        if subset.empty:
            return 0, 0, 0.0
        total_q = subset['qty'].sum()
        total_c = subset['num_for_deck'].sum()
        pct = (total_c / total_q * 100) if total_q > 0 else 0
        return int(total_q), int(total_c), pct

    # Calculate deck completeness (usually based on both main/side, 
    # but kept here for consistency)
    deck_completeness = df_all_decks.groupby('DeckName').apply(
        lambda x: (x['num_for_deck'] >= x['qty']).all()
    )

    # 1. Total "Decks" Row
    all_names = df_battle_box['DeckName'].unique()
    t_q, t_c, t_pct = calc_card_stats(all_names)
    stats_list.append({
        "Cat": "Decks", "nº": len(all_names), "nº complete": deck_completeness[deck_completeness].count(),
        "cards": t_q, "cards collected": t_c, "% cards": t_pct
    })

    # 2. Category Rows
    for cat in categories:
        if cat in ["Aggro", "Midrange", "Tempo", "Control"]:
            cat_decks = df_battle_box[df_battle_box['Archetype'] == cat]['DeckName'].unique()
        else:
            # Assuming 'Meta' or 'Brew' logic
            cat_decks = df_battle_box[df_battle_box['Brew'] == cat]['DeckName'].unique()
        
        c_q, c_c, c_pct = calc_card_stats(cat_decks)
        c_comp = deck_completeness.reindex(cat_decks).fillna(False).sum()
        
        stats_list.append({
            "Cat": cat, "nº": len(cat_decks), "nº complete": int(c_comp),
            "cards": c_q, "cards collected": c_c, "% cards": c_pct
        })

    return pd.DataFrame(stats_list)


# features.py

COLOR_NAME_MAP = {
    frozenset(['W']): 'White', frozenset(['U']): 'Blue', frozenset(['B']): 'Black', 
    frozenset(['R']): 'Red', frozenset(['G']): 'Green',
    frozenset(['W', 'U']): 'Azorius', frozenset(['U', 'B']): 'Dimir', 
    frozenset(['B', 'R']): 'Rakdos', frozenset(['R', 'G']): 'Gruul', 
    frozenset(['G', 'W']): 'Selesnya', frozenset(['W', 'B']): 'Orzhov', 
    frozenset(['U', 'R']): 'Izzet', frozenset(['B', 'G']): 'Golgari', 
    frozenset(['R', 'W']): 'Boros', frozenset(['G', 'U']): 'Simic',
    frozenset(['W', 'U', 'B']): 'Esper', frozenset(['U', 'B', 'R']): 'Grixis', 
    frozenset(['B', 'R', 'G']): 'Jund', frozenset(['R', 'G', 'W']): 'Naya', 
    frozenset(['G', 'W', 'U']): 'Bant', frozenset(['W', 'B', 'G']): 'Abzan', 
    frozenset(['U', 'R', 'W']): 'Jeskai', frozenset(['B', 'G', 'U']): 'Sultai', 
    frozenset(['R', 'W', 'B']): 'Mardu', frozenset(['G', 'U', 'R']): 'Temur'
}

@st.cache_data
def get_color_identity_stats(df_all_decks, df_battle_box, section):
    # 1. Identity based ONLY on the filtered section (e.g., 'main')
    def get_identity(mana_series):
        colors = set()
        all_mana = "".join(mana_series.dropna().astype(str))
        for char in "WUBRG":
            if char in all_mana: colors.add(char)
        if not colors: return "Colorless"
        if len(colors) >= 4: return "4+ Colors"
        return COLOR_NAME_MAP.get(frozenset(colors), "Unknown")

    # Filter by section before calculating identity
    df_filtered = df_all_decks[df_all_decks['section'] == section]
    deck_ids = df_filtered.groupby('DeckName')['mana'].apply(get_identity).reset_index(name='Identity')
    
    # 2. Completeness (Specific to the section)
    completeness = df_filtered.groupby('DeckName').apply(lambda x: (x['num_for_deck'] >= x['qty']).all())

    stats = []
    bb_decks = df_battle_box['DeckName'].unique()
    present_idents = deck_ids[deck_ids['DeckName'].isin(bb_decks)]['Identity'].unique()
    
    for ident in sorted(present_idents):
        names = deck_ids[deck_ids['Identity'] == ident]['DeckName'].unique()
        # Summing data for the specific section only
        sub = df_filtered[df_filtered['DeckName'].isin(names)]
        
        if not sub.empty:
            q, c = sub['qty'].sum(), sub['num_for_deck'].sum()
            stats.append({
                "Identity": ident,
                "nº": len(names),
                "nº complete": int(completeness.reindex(names).fillna(False).sum()),
                "cards": int(q),
                "cards collected": int(c),
                "% cards": (c / q * 100) if q > 0 else 0
            })
    return pd.DataFrame(stats).sort_values("nº", ascending=False)