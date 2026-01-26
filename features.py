import re
import pandas as pd
import streamlit as st

@st.cache_data
def get_stats(df):
    pattern = r'\{(.*?)\}'
    valid_types = ['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment', 'Planeswalker', 'Land', 'Battle']
    
    counts = {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 0, 'Colorless': 0, 'Land': 0}
    values = {'White': 0.0, 'Blue': 0.0, 'Black': 0.0, 'Red': 0.0, 'Green': 0.0, 'Colorless': 0.0, 'Land': 0.0}
    type_counts = {t: 0 for t in valid_types}; type_values = {t: 0.0 for t in valid_types}
    cmc_counts = {}; cmc_values = {}

    if df is None or df.empty:
        return pd.DataFrame(columns=['Color', 'Count', 'Value']), \
               pd.DataFrame(columns=['Type', 'Count', 'Value']), \
               pd.DataFrame(columns=['CMC', 'Count', 'Value'])

    for _, row in df.iterrows():
        qty = int(row.get('Qty', 1))
        total_val = float(row.get('Total', 0.0))
        mana_str = str(row.get('Mana', '')).strip()
        type_line = str(row.get('Type', ''))
        
        # --- 1. Types Logic ---
        found_types = [t for t in valid_types if t in type_line]
        if found_types:
            val_per_type = total_val / len(found_types)
            for t in found_types:
                type_counts[t] += qty
                type_values[t] += val_per_type

        # --- 2. Color Identity Logic ---
        symbols = re.findall(pattern, mana_str)
        if symbols:
            # Check for WUBRG
            color_map = {'W':'White', 'U':'Blue', 'B':'Black', 'R':'Red', 'G':'Green'}
            unique_colors = {color_map[c] for s in symbols for c in color_map if c in s.upper()}
            
            if unique_colors:
                val_per_color = total_val / len(unique_colors)
                for color in unique_colors:
                    counts[color] += qty
                    values[color] += val_per_color
            else:
                # Symbols exist but no WUBRG (e.g., {C} or {S}) -> Colorless
                counts['Colorless'] += qty
                values['Colorless'] += total_val
        else:
            # No symbols -> Lands go to Land, everything else (Artifacts) goes to Colorless
            key = 'Land' if "Land" in type_line else 'Colorless'
            counts[key] += qty
            values[key] += total_val

        # --- 3. CMC Logic (Non-lands) ---
        if "Land" not in type_line:
            # Handle split cards for CMC
            primary_mana = mana_str.split('//')[0].strip()
            primary_symbols = re.findall(pattern, primary_mana)
            cmc = sum(int(s) if s.isdigit() else 1 for s in primary_symbols if s)
            cmc_counts[cmc] = cmc_counts.get(cmc, 0) + qty
            cmc_values[cmc] = cmc_values.get(cmc, 0.0) + total_val

    # Construct DataFrames with fallback columns to prevent KeyErrors
    df_color = pd.DataFrame([{'Color': k, 'Count': counts[k], 'Value': values[k]} for k in counts if counts[k] > 0])
    if df_color.empty: df_color = pd.DataFrame(columns=['Color', 'Count', 'Value'])

    df_type = pd.DataFrame([{'Type': k, 'Count': type_counts[k], 'Value': type_values[k]} for k in type_counts if type_counts[k] > 0])
    df_type = df_type.sort_values(by='Count', ascending=False) if not df_type.empty else pd.DataFrame(columns=['Type', 'Count', 'Value'])

    df_cmc = pd.DataFrame([{'CMC': k, 'Count': v, 'Value': cmc_values[k]} for k, v in cmc_counts.items()])
    df_cmc = df_cmc.sort_values(by='CMC') if not df_cmc.empty else pd.DataFrame(columns=['CMC', 'Count', 'Value'])

    return df_color, df_type, df_cmc


@st.cache_data
def get_land_breakdown(df):
    # Initialize dictionaries for counts and actual total values
    cat = {'Basic':0, 'Snow':0, 'Dual Basics':0, 'Snow Duals':0, 'Artifact Lands':0, 'Others':0}
    vals = {'Basic':0.0, 'Snow':0.0, 'Dual Basics':0.0, 'Snow Duals':0.0, 'Artifact Lands':0.0, 'Others':0.0}
    
    basic_types = ['Plains', 'Island', 'Swamp', 'Mountain', 'Forest']
    
    # Filter for lands
    lands = df[df['Type'].str.contains('Land', na=False, case=False)]
    
    for _, row in lands.iterrows():
        t = str(row.get('Type', ''))
        n = str(row.get('Name', ''))
        q = int(row.get('Qty', 1))
        # Use the 'Total' column which should already be Qty * Price
        v = float(row.get('Total', 0.0))
        
        is_snow = "Snow" in t or "Snow" in n
        # Count occurrences of basic types in the type line
        type_count = sum(1 for bt in basic_types if bt in t)
        is_dual = type_count >= 2
        
        if "Artifact" in t: 
            k = 'Artifact Lands'
        elif is_snow and is_dual: 
            k = 'Snow Duals'
        elif is_dual: 
            k = 'Dual Basics'
        elif is_snow: 
            k = 'Snow'
        elif "Basic" in t or any(bt == t.strip() for bt in basic_types): 
            k = 'Basic'
        else: 
            k = 'Others'
        
        cat[k] += q
        vals[k] += v
        
    # Build DataFrame from the summed values
    return pd.DataFrame([
        {'Stat': k, 'Count': cat[k], 'Value': vals[k]} 
        for k in cat.keys()
    ])


@st.cache_data
def get_set_stats(df):
    return df.groupby('Edition').agg(Count=('Qty', 'sum'), Value=('Total', 'sum')).reset_index()

@st.cache_data
def get_rarity_stats(df):
    return df.groupby('Rarity').agg(Count=('Qty', 'sum'), Value=('Total', 'sum')).reset_index()