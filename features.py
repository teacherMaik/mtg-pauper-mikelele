import re
import pandas as pd

def get_sidebar_stats(df):
    # --- SETUP ---
    pattern = r'\{(.*?)\}'
    valid_types = ['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment', 'Planeswalker', 'Land', 'Battle']
    
    # Initialize Color Dictionaries
    counts = {'White': 0, 'Blue': 0, 'Black': 0, 'Red': 0, 'Green': 0, 'Colorless': 0}
    values = {'White': 0.0, 'Blue': 0.0, 'Black': 0.0, 'Red': 0.0, 'Green': 0.0, 'Colorless': 0.0}
    
    # Initialize Type Dictionary
    type_counts = {t: 0 for t in valid_types}

    # --- SINGLE PASS ITERATION ---
    for _, row in df.iterrows():
        qty = int(row.get('Qty', 1))
        card_total = float(row.get('Total', 0.0))
        mana_str = str(row.get('Mana', ''))
        type_line = str(row.get('Type', ''))

        # 1. Process Types (Simple check)
        for t in valid_types:
            if t in type_line:
                type_counts[t] += qty

        # 2. Process Colors (Strict rules)
        symbols = re.findall(pattern, mana_str)
        if symbols:
            found_colors = []
            for s in symbols:
                s = s.upper()
                if 'W' in s: found_colors.append('White')
                elif 'U' in s: found_colors.append('Blue')
                elif 'B' in s: found_colors.append('Black')
                elif 'R' in s: found_colors.append('Red')
                elif 'G' in s: found_colors.append('Green')

            if found_colors:
                # Add Pips
                for color in found_colors:
                    counts[color] += qty
                # Split Value
                val_per_pip = card_total / len(found_colors)
                for color in found_colors:
                    values[color] += val_per_pip
            elif len(symbols) == 1:
                # Pure Colorless check
                s = symbols[0].upper()
                if s.isdigit() or s in ['C', 'X']:
                    counts['Colorless'] += qty
                    values['Colorless'] += card_total

    # --- PREPARE DATA FOR PLOTS ---
    df_color = pd.DataFrame([{'Color': k, 'Count': counts[k], 'Value': values[k]} for k in counts if counts[k] > 0])
    df_type = pd.DataFrame([{'Type': k, 'Count': v} for k, v in type_counts.items() if v > 0]).sort_values(by='Count')

    return df_color, df_type