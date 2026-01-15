# features.py
import re
import pandas as pd

def get_color_distribution(df):
    """Parses Mana column to count color pips weighted by Qty."""
    pattern = r'\{(.*?)\}'
    color_counts_dict = {
        'White': 0, 'Blue': 0, 'Black': 0, 
        'Red': 0, 'Green': 0, 'Colorless': 0
    }

    for _, row in df.iterrows():
        mana_str = str(row.get('Mana', ''))
        qty = row.get('Qty', 1)
        
        symbols = re.findall(pattern, mana_str)
        
        for s in symbols:
            if 'W' in s: color_counts_dict['White'] += qty
            elif 'U' in s: color_counts_dict['Blue'] += qty
            elif 'B' in s: color_counts_dict['Black'] += qty
            elif 'R' in s: color_counts_dict['Red'] += qty
            elif 'G' in s: color_counts_dict['Green'] += qty
            # Catches {1}, {2}, {C}, {X}
            elif s.isdigit() or s in ['C', 'X']: 
                color_counts_dict['Colorless'] += qty

    return pd.DataFrame(list(color_counts_dict.items()), columns=['Color', 'Count'])