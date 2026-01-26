import re
import pandas as pd

def get_stats(df):
    """The 'Engine' - Iterates once and returns all necessary DataFrames."""
    # --- SETUP ---
    pattern = r'\{(.*?)\}'
    valid_types = ['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment', 'Planeswalker', 'Land', 'Battle']
    
    counts = {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 0, 'Colorless': 0, 'Land': 0}
    values = {'White': 0.0, 'Blue': 0.0, 'Black': 0.0, 'Red': 0.0, 'Green': 0.0, 'Colorless': 0.0, 'Land': 0.0}
    
    type_counts = {t: 0 for t in valid_types}
    type_values = {t: 0.0 for t in valid_types}

    for _, row in df.iterrows():
        qty = int(row.get('Qty', 1))
        card_total = float(row.get('Total', 0.0))
        mana_str = str(row.get('Mana', '')).strip()
        type_line = str(row.get('Type', ''))

        # 1. Process Types (Split value for multi-type like Artifact Creature)
        found_types = [t for t in valid_types if t in type_line]
        if found_types:
            val_per_type = card_total / len(found_types)
            for t in found_types:
                type_counts[t] += qty
                type_values[t] += val_per_type

        # 2. Process Colors 
        symbols = re.findall(pattern, mana_str)
        
        # Land Logic: Non-mana-producing lands go to 'Land' bucket
        if "Land" in type_line and not any(c in mana_str.upper() for c in 'WUBRG'):
            counts['Land'] += qty
            values['Land'] += card_total
        elif symbols:
            unique_colors_in_card = set()
            for s in symbols:
                s = s.upper()
                if 'W' in s: unique_colors_in_card.add('White')
                if 'U' in s: unique_colors_in_card.add('Blue')
                if 'B' in s: unique_colors_in_card.add('Black')
                if 'R' in s: unique_colors_in_card.add('Red')
                if 'G' in s: unique_colors_in_card.add('Green')

            if unique_colors_in_card:
                val_per_color = card_total / len(unique_colors_in_card)
                for color in unique_colors_in_card:
                    counts[color] += qty
                    values[color] += val_per_color
            else: # Has symbols but none are WUBRG (e.g., {C} or {1})
                counts['Colorless'] += qty
                values['Colorless'] += card_total
        else: # No mana symbols (True Colorless artifacts)
            counts['Colorless'] += qty
            values['Colorless'] += card_total

    # --- PREPARE DATA ---
    df_color = pd.DataFrame([{'Color': k, 'Count': counts[k], 'Value': values[k]} for k in counts if counts[k] > 0])
    df_type = pd.DataFrame([{'Type': k, 'Count': type_counts[k], 'Value': type_values[k]} for k in type_counts if type_counts[k] > 0]).sort_values(by='Count')

    return df_color, df_type

# --- HELPER FUNCTIONS (The ones you call in the UI) ---

def get_rarity_stats(df):
    """Returns aggregated rarity data."""
    rarity_data = df.groupby('Rarity').agg(
        Count=('Qty', 'sum'),
        Value=('Total', 'sum')
    ).reset_index()

    rarity_data = rarity_data.sort_values(by='Count', ascending=False)
    return rarity_data

def get_cmc_stats(df):
    """Returns data for a Mana Curve chart."""
    # Ensure CMC is numeric
    df['CMC'] = pd.to_numeric(df['CMC'], errors='coerce').fillna(0)
    return df.groupby('CMC')['Qty'].sum().reset_index()

def get_set_stats(df):
    """Returns aggregated set data."""
    set_data = df.groupby('Edition').agg(
        Count=('Qty', 'sum'),
        Value=('Total', 'sum')
    ).reset_index()

    set_data = set_data.sort_values(by='Count', ascending=False)
    return set_data