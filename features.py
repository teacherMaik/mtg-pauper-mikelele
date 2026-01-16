import re
import pandas as pd

def get_sidebar_stats(df):
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

        # 1. Process Types
        found_types = [t for t in valid_types if t in type_line]
        if found_types:
            val_per_type = card_total / len(found_types)
            for t in found_types:
                type_counts[t] += qty
                type_values[t] += val_per_type

        # 2. Process Colors (Unique Color Identity Logic)
        symbols = re.findall(pattern, mana_str)
        
        if "Land" in type_line and not any(c in mana_str.upper() for c in 'WUBRG'):
            counts['Land'] += qty
            values['Land'] += card_total
        elif symbols:
            # Use a SET to store unique colors found in this specific card's mana cost
            unique_colors_in_card = set()
            is_truly_colorless = True

            for s in symbols:
                s = s.upper()
                if 'W' in s: unique_colors_in_card.add('White'); is_truly_colorless = False
                if 'U' in s: unique_colors_in_card.add('Blue'); is_truly_colorless = False
                if 'B' in s: unique_colors_in_card.add('Black'); is_truly_colorless = False
                if 'R' in s: unique_colors_in_card.add('Red'); is_truly_colorless = False
                if 'G' in s: unique_colors_in_card.add('Green'); is_truly_colorless = False

            if unique_colors_in_card:
                # Add 1 to count for each color found (regardless of pip amount)
                for color in unique_colors_in_card:
                    counts[color] += qty
                
                # Split value across the unique colors found
                val_per_color = card_total / len(unique_colors_in_card)
                for color in unique_colors_in_card:
                    values[color] += val_per_color
            elif is_truly_colorless:
                counts['Colorless'] += qty
                values['Colorless'] += card_total

    # --- PREPARE DATA ---
    df_color = pd.DataFrame([{'Color': k, 'Count': counts[k], 'Value': values[k]} for k in counts if counts[k] > 0])
    df_type = pd.DataFrame([{'Type': k, 'Count': type_counts[k], 'Value': type_values[k]} for k in type_counts if type_counts[k] > 0]).sort_values(by='Count')

    return df_color, df_type