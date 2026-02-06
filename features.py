import re
import pandas as pd
import streamlit as st
import maps_utilities
import plotly.graph_objects as go
import plotly.express as px


METALLIC_GRAY = "#2c3e50"
LIGHT_GRAY = "#90ADBB"
POP_GOLD = "#FFD700"
BORDER_COLOR = "#1a1a1a"


@st.cache_data
def get_top_sets_donut(df, sort_metric, view_mode):
    
    df_sets = df.copy()

    # 1. Apply Count Mode Logic
    if view_mode == "Unique":
        df_sets['qty'] = 1
        if 'price' in df_sets.columns:
            df_sets['total_cards_value'] = df_sets['price']

    # 2. Grouping & Selecting Top 12
    # Use 'qty' or 'total_cards_value' based on sort_metric radio button
    col_key = 'qty' if sort_metric == "Qty" else 'total_cards_value'
    
    set_data = df_sets.groupby('edition').agg(
        qty=('qty', 'sum'),
        total_cards_value=('total_cards_value', 'sum')
    ).reset_index().sort_values(by=col_key, ascending=False).head(12)

    if set_data.empty:
        return None

    # 12-shade Metallic Gray Palette
    metallic_rgba = [
        'rgba(44, 62, 80, 1.0)', 'rgba(44, 62, 80, 0.9)', 'rgba(44, 62, 80, 0.8)',
        'rgba(44, 62, 80, 0.7)', 'rgba(44, 62, 80, 0.6)', 'rgba(44, 62, 80, 0.5)',
        'rgba(44, 62, 80, 0.45)', 'rgba(44, 62, 80, 0.4)', 'rgba(44, 62, 80, 0.35)',
        'rgba(44, 62, 80, 0.3)', 'rgba(44, 62, 80, 0.25)', 'rgba(44, 62, 80, 0.2)'
    ]

    # 4. Create the Donut Chart
    fig = px.pie(
        set_data, 
        values=col_key, 
        names='edition', 
        hole=0.42, 
        color_discrete_sequence=metallic_rgba
    )

    # 5. Dynamic Hover Template based on metric
    hover_template = "<b>%{label}</b><br>Qty: %{value}<extra></extra>" if sort_metric == "Qty" \
             else "<b>%{label}</b><br>Value: $%{value:.2f}<extra></extra>"

    fig.update_traces(
        hovertemplate=hover_template,
        marker=dict(line=dict(color='white', width=1)),
        textinfo='percent'
    )

    fig.update_layout(
        showlegend=True, 
        legend=dict(
            orientation="h", 
            yanchor="top", 
            y=-0.14, 
            xanchor="center", 
            x=0.5
        ), 
        height=450, 
        margin=dict(t=10, b=80, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )
    
    return fig


@st.cache_data
def get_color_saturation_widget(
    df,
    is_transposed,
    rarity_select,
    count_select='All',
    is_deck=None):
    
    # Make copy of passed DF excluding Lands
    df_colors = df[df['color'] != 'L'].copy()

    # Deck Section Logic (if is_deck is passed, then Specific Deck Stats)
    if is_deck and is_deck != 'Both' and 'section' in df_colors.columns:

        # Internal map so the UI can send "Main" and we use "main"
        section_map = {
            'Main': 'main',
            'Side': 'sideboard'
        }

        db_val = section_map.get(is_deck, is_deck) # Fallback to original if not in map
        df_colors = df_colors[df_colors['section'] == db_val]

    # Rarity Mapping (Present for Battle Box, Inventory and Deck Stats)
    if rarity_select:

        rarity_map = {
            'Common': 'Common',
            'Uncommon': 'Uncommon',
            'Rare': 'Rare',
            'Mythic': 'MythicRare'
        }

        df_colors = df_colors[df_colors['rarity'].isin([rarity_map[r] for r in rarity_select])]

    # Unique/All Cards Filter mode ("All" by default, no need to pass from Deck Stats view)
    if count_select == "Unique":
        df_colors['qty'] = 1
        if 'price' in df_colors.columns:
            df_colors['total_cards_value'] = df_colors['price']

    # Sum of ALL qty of cards in DF (Important for calculating %)
    grand_total_qty = df_colors['qty'].sum()
    
    # Map colors to represent mtg colors
    colors_map = {
        'W': '#F0F2F0',
        'U': '#0E68AB',
        'B': '#150B00',
        'R': '#D3202A',
        'G': '#00733E',
        'C': LIGHT_GRAY,
        'Multi': POP_GOLD
    }

    categories = [
        ('W','White'),
        ('U','Blue'),
        ('B','Black'),
        ('R','Red'),
        ('G','Green'),
        ('C','Colorless'),
        ('Multi','Multicolor')
    ]
    
    # Declare Figure and tranpose orientation
    fig = go.Figure()
    bar_orient = 'h' if is_transposed else 'v'

    # If no data, return None to display info message
    if df_colors.empty:
        return None  # Or False

    # Loop through categories
    for code, name in categories:

        # We use string with all 5 colors. df['color'] could be BW, B, URG...
        if code in 'WUBRG':

            # Count card for each color. total card count will be higher than collection
            df_mono_colored = df_colors[(df_colors['color'] == code) & (df_colors['is_multi_colored'] == False)]

            # If card has multiple colors, we add to "multi"
            df_mutli_colored = df_colors[(df_colors['color'].str.contains(code, na=False)) & (df_colors['is_multi_colored'] == True)]

        elif code == 'C':

            # If no colors found, then set mono colored to Colorless and multi_colored to "empty"
            df_mono_colored = df_colors[df_colors['color'] == 'C']
            df_mutli_colored = df_colors.iloc[0:0]
        else:
            # Handle the 'Multi' category: Show all multi-colored cards as one group
            df_mono_colored = df_colors.iloc[0:0]  # Returns an empty DataFrame
            df_mutli_colored = df_colors[df_colors['is_multi_colored'] == True]

        # Get total cards of color in question and total of multi-colored with that color
        qty_mono, qty_multi = df_mono_colored['qty'].sum(), df_mutli_colored['qty'].sum()

        # Calculate their respective values for hover display
        value_mono = df_mono_colored['total_cards_value'].sum() if 'total_cards_value' in df_mono_colored.columns else 0
        value_multi = df_mutli_colored['total_cards_value'].sum() if 'total_cards_value' in df_mutli_colored.columns else 0
        
        # Total pips and their value counting pure color + multi-color part
        total_present_val = value_mono + value_multi
        total_present_qty = qty_mono + qty_multi

        # Calc % of colored pips in terms of entire collection in DF.
        collection_percent = (total_present_qty / grand_total_qty * 100) if grand_total_qty > 0 else 0

        # Calc remainder of cards after total pips, to paint Dark Gray
        remainder_qty = grand_total_qty - total_present_qty

        # Utility function to add segment (3 segments) to  each bar (7 bars) in figure
        def add_seg(s_name, val, col, hover_template):
            if val <= 0: return
            x_v, y_v = ([val], [name]) if is_transposed else ([name], [val])
            fig.add_trace(go.Bar(
                name=s_name, x=x_v, y=y_v, orientation=bar_orient,
                marker=dict(color=col, line=dict(color=BORDER_COLOR, width=1.5)),
                hovertemplate=hover_template, showlegend=False))
            
        
        # Color segment starts at bottom
        add_seg(
            name,
            qty_mono,
            colors_map[code],
            f"<b>{name}</b><br>Qty: {qty_mono}<br>Value: ${value_mono:,.2f}<extra></extra>")

        # Multi colored Segment stacks on top (colorless will have no multi seg and in the Multi bar, will start at bottom)
        add_seg(
            "Multi",
            qty_multi,
            POP_GOLD,
            f"<b>Multi</b><br>Qty: +{qty_multi}<br>Value: +${value_multi:,.2f}<extra></extra>")

        # Remainder seg will repesent all cards in collection not having pisp of color
        add_seg(
            "Remainder",
            remainder_qty, METALLIC_GRAY,
            f"<b>{name} Pips</b><br>% of Cards: {collection_percent:.1f}%<br>Total Value: ${total_present_val:,.2f}<extra></extra>")

    fig.update_layout(
        barmode='stack',
        height=550 if not is_transposed else 450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=50, l=10, r=10)
    )

    if is_transposed: fig.update_yaxes(autorange="reversed")

    return fig


@st.cache_data
def get_type_distribution_widget(
    df,
    color_select,
    count_select='All',
    is_deck=None):
    
    # Copy DF as is, no filtering out Lands
    df_types = df.copy()

    # Deck Section Logic (if is_deck is passed, then Specific Deck Stats)
    if is_deck and is_deck != 'Both' and 'section' in df_types.columns:

        # Internal map so the UI can send "Main" and we use "main"
        section_map = {
            'Main': 'main',
            'Side': 'sideboard'
        }

        db_val = section_map.get(is_deck, is_deck) # Fallback to original if not in map
        df_types = df_types[df_types['section'] == db_val]

    # Unique/All Cards Filter mode ("All" by default, no need to pass from Deck Stats view)
    if count_select == "Unique":
        df_types['qty'] = 1
        if 'price' in df_types.columns:
            df_types['total_cards_value'] = df_types['price']

    # Color Filter Logic
    if color_select:

        ui_to_db = {
            'White': 'W',
            'Blue': 'U',
            'Black': 'B',
            'Red': 'R',
            'Green': 'G',
            'Colorless': 'C'
        }

        codes = [ui_to_db[c] for c in color_select if c in ui_to_db]
        wants_multi = 'Multicolor' in color_select

        pattern = '|'.join(codes) if codes else None

        mask = df_types['color'].str.contains(pattern, na=False) if pattern else pd.Series(False, index=df_types.index)

        if wants_multi: 
            mask = mask | (df_types['is_multi_colored'] == True)

        df_types = df_types[mask]

    if df_types.empty:
        return None

    valid_types = [
        'Creature',
        'Instant',
        'Sorcery',
        'Artifact',
        'Enchantment',
        'Planeswalker',
        'Land',
        'Battle'
    ]

    rows = []

    for type in valid_types:

        subset = df_types[df_types['type'].str.contains(type, na=False, case=False)]

        if not subset.empty:

            rows.append({
                'Type': type,
                'Count': int(subset['qty'].sum()),
                'Value': subset['total_cards_value'].sum()
            })

    type_data = pd.DataFrame(rows)

    if type_data.empty:
        return None
    
    # 8-shade Metallic Gray Palette
    metallic_rgba = [
        'rgba(44, 62, 80, 1.0)',
        'rgba(44, 62, 80, 0.9)',
        'rgba(44, 62, 80, 0.8)',
        'rgba(44, 62, 80, 0.7)',
        'rgba(44, 62, 80, 0.6)',
        'rgba(44, 62, 80, 0.5)',
        'rgba(44, 62, 80, 0.4)',
        'rgba(44, 62, 80, 0.3)',
        'rgba(44, 62, 80, 0.2)',
        'rgba(44, 62, 80, 0.1)'
        ]
    
    fig = px.pie(
        type_data.sort_values(by='Count', ascending=False),
        values='Count',
        names='Type',
        hole=0.42,
        custom_data=['Value'],
        color_discrete_sequence=metallic_rgba
    )

    fig.update_traces(
        textposition='inside',
        textinfo='percent',
        hovertemplate="<b>%{label}</b><br>Qty: %{value}<br>Total Value: $%{customdata[0]:,.2f}<extra></extra>",
        marker=dict(line=dict(color='white', width=1))
    )

    fig.update_layout(
        showlegend=True,
        legend=dict(orientation="h", yanchor="top", y=-0.14, xanchor="center", x=0.5),
        height=450,
        margin=dict(t=10, b=80, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)'
    )

    return fig


def get_mana_curve_widget(df, page_view, is_transposed, sel_type=None, sel_color=None):
    """
    Standardized Mana Curve Logic.
    page_view: 'Inventory', 'Deck View', or 'Deck Test'
    """
    if df is None or df.empty:
        return None

    # 1. Filter out Lands
    df_f = df[df['primary_type_for_deck'] != 'Land'].copy()

    # 2. Apply Filters (if provided)
    if sel_type:
        df_f = df_f[df_f['primary_type_for_deck'].isin(sel_type)]
    if sel_color:
        ui_to_db = {'White':'W', 'Blue':'U', 'Black':'B', 'Red':'R', 'Green':'G', 'Colorless':'C'}
        codes = [ui_to_db[c] for c in sel_color if c in ui_to_db]
        pattern = '|'.join(codes)
        df_f = df_f[df_f['color'].str.contains(pattern, na=False)]

    if df_f.empty:
        return None

    # 3. Labeling & Sorting (X handling)
    df_f['chart_label'] = df_f.apply(lambda x: 'X' if x['cmc_has_x'] else str(int(x['cmc'])), axis=1)
    df_f['chart_sort'] = df_f.apply(lambda x: 99 if x['cmc_has_x'] else int(x['cmc']), axis=1)

    # 4. Aggregation
    agg_map = {'qty': 'sum', 'total_cards_value': 'sum'}
    
    # Contextual Hover Data
    if 'Deck' in page_view:
        agg_map['name'] = lambda x: "<br>".join([f"• {n}" for n in sorted(x.unique())])
    else:
        agg_map['name'] = lambda x: ""

    curve_data = df_f.groupby(['chart_label', 'chart_sort']).agg(agg_map).reset_index()
    curve_data = curve_data.sort_values('chart_sort', ascending=not is_transposed)

    # 5. Plotly Render
    METALLIC_GRAY = '#2c3e50' 
    x_col, y_col = ('qty', 'chart_label') if is_transposed else ('chart_label', 'qty')
    
    fig = px.bar(
        curve_data, x=x_col, y=y_col, 
        orientation='h' if is_transposed else 'v',
        text_auto=True, 
        custom_data=['total_cards_value', 'name']
    )

    l_ref = "%{y}" if is_transposed else "%{x}"
    q_ref = "%{x}" if is_transposed else "%{y}"
    
    # --- DYNAMIC HOVER CONSTRUCTION ---
    # Start with CMC and Qty
    hover_tmpl = f"<b>CMC {l_ref}</b><br>Qty: {q_ref}"
    
    # Only add Value if NOT in Deck Test mode
    if page_view != 'Deck Test':
        hover_tmpl += f"<br>Value: $%{'{customdata[0]:,.2f}'}"
    
    # Add Card Names for any Deck-related view
    if 'Deck' in page_view:
        hover_tmpl += "<br><br><b>Cards:</b><br>%{customdata[1]}"
    
    fig.update_traces(
        marker_color=METALLIC_GRAY, 
        hovertemplate=hover_tmpl + "<extra></extra>"
    )

    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title=None, yaxis_title=None,
        xaxis={'type': 'category'} if not is_transposed else None,
        yaxis={'type': 'category'} if is_transposed else None
    )

    return fig


@st.cache_data
def summarize_battle_box(df_battle_box, df_all_decks, section):
    """Aggregates completion percentages by Brew/Meta and Archetype."""
    categories = ["Meta", "Brew", "Aggro", "Midrange", "Tempo", "Control", "Combo"]
    stats_list = []

    def calc_card_stats(deck_names):
        mask = (df_all_decks['DeckName'].isin(deck_names)) & \
               (df_all_decks['section'].str.contains(section, case=False, na=False))
        subset = df_all_decks[mask]
        if subset.empty: return 0, 0, 0.0
        q, c = subset['qty'].sum(), subset['num_for_deck'].sum()
        return int(q), int(c), (c / q * 100) if q > 0 else 0

    deck_completeness = df_all_decks.groupby('DeckName').apply(lambda x: (x['num_for_deck'] >= x['qty']).all())

    # Total Decks Row
    all_names = df_battle_box['DeckName'].unique()
    t_q, t_c, t_pct = calc_card_stats(all_names)
    stats_list.append({"Cat": "Total", "nº": len(all_names), "nº complete": int(deck_completeness.sum()), 
                       "cards": t_q, "cards collected": t_c, "% cards": t_pct})

    for cat in categories:
        col = 'Archetype' if cat in ["Aggro", "Midrange", "Tempo", "Control", "Combo"] else 'Brew'
        cat_decks = df_battle_box[df_battle_box[col] == cat]['DeckName'].unique()
        c_q, c_c, c_pct = calc_card_stats(cat_decks)
        c_comp = deck_completeness.reindex(cat_decks).fillna(False).sum()
        stats_list.append({"Cat": cat, "nº": len(cat_decks), "nº complete": int(c_comp), 
                           "cards": c_q, "cards collected": c_c, "% cards": c_pct})

    return pd.DataFrame(stats_list)


@st.cache_data
def filter_land_cards(df):
    """Returns only cards that are lands, including MDFCs."""
    if df is None or df.empty: return pd.DataFrame()
    return df[df['type'].str.contains('Land', na=False, case=False)]









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
