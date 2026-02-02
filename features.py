import re
import pandas as pd
import streamlit as st
import utility_maps
import plotly.graph_objects as go
import plotly.express as px


@st.cache_data
def get_color_saturation_widget(df, rarity_select, count_select, is_transposed):
    """Handles logic and plotting for the Color Saturation Bar Chart."""
    df_colors = df[df['color'] != 'L'].copy()

    # Rarity Mapping
    if rarity_select:
        rarity_map = {'Common': 'Common', 'Uncommon': 'Uncommon', 'Rare': 'Rare', 'Mythic': 'MythicRare'}
        df_colors = df_colors[df_colors['rarity'].isin([rarity_map[r] for r in rarity_select])]

    # Unique Mode
    if count_select == "Unique":
        df_colors['qty'] = 1
        if 'price' in df_colors.columns:
            df_colors['total_cards_value'] = df_colors['price']

    grand_total_qty = df_colors['qty'].sum()
    METALLIC_GRAY, LIGHT_GRAY, POP_GOLD, BORDER_COLOR = "#2c3e50", "#90ADBB", "#FFD700", "#1a1a1a"
    colors_map = {'W': '#F0F2F0', 'U': '#0E68AB', 'B': '#150B00', 'R': '#D3202A', 'G': '#00733E', 'C': LIGHT_GRAY, 'Multi': POP_GOLD}
    categories = [('W','White'), ('U','Blue'), ('B','Black'), ('R','Red'), ('G','Green'), ('C','Colorless'), ('Multi','Multicolor')]
    
    fig = go.Figure()
    bar_orient = 'h' if is_transposed else 'v'

    for code, name in categories:
        if code in 'WUBRG':
            df_mono_colored = df_colors[(df_colors['color'] == code) & (df_colors['is_multi_colored'] == False)]
            df_mutli_colored = df_colors[(df_colors['color'].str.contains(code, na=False)) & (df_colors['is_multi_colored'] == True)]
        elif code == 'C':
            df_mono_colored = df_colors[df_colors['color'] == 'C']; df_mutli_colored = df_colors.iloc[0:0]
        else:
            df_mono_colored = df_colors.iloc[0:0]; df_mutli_colored = df_colors[df_colors['is_multi_colored'] == True]

        qty_mono, qty_multi = df_mono_colored['qty'].sum(), df_mutli_colored['qty'].sum()
        value_mono = df_mono_colored['total_cards_value'].sum() if 'total_cards_value' in df_mono_colored.columns else 0
        value_multi = df_mutli_colored['total_cards_value'].sum() if 'total_cards_value' in df_mutli_colored.columns else 0
        
        total_present_val = value_mono + value_multi
        total_present_qty = qty_mono + qty_multi
        collection_percent = (total_present_qty / grand_total_qty * 100) if grand_total_qty > 0 else 0
        remainder_qty = grand_total_qty - total_present_qty

        def add_seg(s_name, val, col, h_temp):
            if val <= 0: return
            x_v, y_v = ([val], [name]) if is_transposed else ([name], [val])
            fig.add_trace(go.Bar(
                name=s_name, x=x_v, y=y_v, orientation=bar_orient,
                marker=dict(color=col, line=dict(color=BORDER_COLOR, width=1.5)),
                hovertemplate=h_temp, showlegend=False))

        add_seg(name, qty_mono, colors_map[code], f"<b>{name}</b><br>Qty: {qty_mono}<br>Value: ${value_mono:,.2f}<extra></extra>")
        add_seg("Multi", qty_multi, POP_GOLD, f"<b>Multi</b><br>Qty: +{qty_multi}<br>Value: +${value_multi:,.2f}<extra></extra>")
        add_seg("Remainder", remainder_qty, METALLIC_GRAY, f"<b>{name} Pips</b><br>Saturation: {collection_percent:.1f}%<br>Total Value: ${total_present_val:,.2f}<extra></extra>")

    fig.update_layout(barmode='stack', height=550 if not is_transposed else 450, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(t=10, b=50, l=10, r=10))
    if is_transposed: fig.update_yaxes(autorange="reversed")
    return fig


@st.cache_data
def get_type_distribution_widget(df, color_select, count_select):
    """Handles logic and plotting for the Type Donut Chart."""
    df_types = df.copy()

    # Unique Mode
    if count_select == "Unique":
        df_types['qty'] = 1
        if 'price' in df_types.columns:
            df_types['total_cards_value'] = df_types['price']

    # Color Filter Logic
    if color_select:
        ui_to_db = {'White': 'W', 'Blue': 'U', 'Black': 'B', 'Red': 'R', 'Green': 'G', 'Colorless': 'C'}
        codes = [ui_to_db[c] for c in color_select if c in ui_to_db]
        wants_multi = 'Multicolor' in color_select
        pattern = '|'.join(codes) if codes else None
        mask = df_types['color'].str.contains(pattern, na=False) if pattern else pd.Series(False, index=df_types.index)
        if wants_multi: mask = mask | (df_types['is_multi_colored'] == True)
        df_types = df_types[mask]

    # Use your existing summary feature to handle multi-type cards
    from features import summarize_by_type
    type_data = summarize_by_type(df_types)
    
    if type_data.empty: return None

    metallic_rgba = ['rgba(44, 62, 80, 1.0)', 'rgba(44, 62, 80, 0.9)', 'rgba(44, 62, 80, 0.8)', 'rgba(44, 62, 80, 0.7)', 'rgba(44, 62, 80, 0.6)', 'rgba(44, 62, 80, 0.5)', 'rgba(44, 62, 80, 0.4)', 'rgba(44, 62, 80, 0.3)', 'rgba(44, 62, 80, 0.2)', 'rgba(44, 62, 80, 0.1)']
    
    fig = px.pie(type_data.sort_values(by='Count', ascending=False), values='Count', names='Type', hole=0.42, custom_data=['Value'], color_discrete_sequence=metallic_rgba)
    fig.update_traces(textposition='inside', textinfo='percent', hovertemplate="<b>%{label}</b><br>Qty: %{value}<br>Total Value: $%{customdata[0]:,.2f}<extra></extra>", marker=dict(line=dict(color='white', width=1)))
    fig.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="top", y=-0.14, xanchor="center", x=0.5), height=450, margin=dict(t=10, b=80, l=10, r=10), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    return fig


@st.cache_data
def summarize_by_type(df):
    """Summarizes qty/value by primary card types."""
    if df is None or df.empty: return pd.DataFrame()

    valid_types = ['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment', 'Planeswalker', 'Land', 'Battle']
    rows = []
    for t in valid_types:
        subset = df[df['type'].str.contains(t, na=False, case=False)]
        if not subset.empty:
            rows.append({
                'Type': t,
                'Count': int(subset['qty'].sum()),
                'Value': subset['total_cards_value'].sum()
            })
    return pd.DataFrame(rows).sort_values(by='Count', ascending=True)


@st.cache_data
def summarize_by_cmc(df):
    """Summarizes CMC distribution, excluding lands."""
    if df is None or df.empty: return pd.DataFrame()
    
    df_non_land = df[~df['type'].str.contains('Land', na=False, case=False)]
    if df_non_land.empty: return pd.DataFrame()

    return df_non_land.groupby('cmc').agg(
        Count=('qty', 'sum'), 
        Value=('total_cards_value', 'sum')
    ).reset_index().rename(columns={'cmc': 'CMC'})


@st.cache_data
def get_mana_curve_widget(df, sel_type, sel_color, is_transposed):
    """
    Handles Type/Color filtering and generates the Metallic Mana Curve Bar Chart.
    """
    df_f = df.copy()
    METALLIC_GRAY = "#2c3e50"

    # 1. Type Filtering
    if sel_type:
        df_f = df_f[df_f['type'].str.contains('|'.join(sel_type), case=False, na=False)]
            
    # 2. Color Filtering (Matches {W}{B} and {WB} logic)
    if sel_color:
        ui_to_db = {
            'White': 'W', 'Blue': 'U', 'Black': 'B', 
            'Red': 'R', 'Green': 'G', 'Colorless': 'C'
        }
        selected_codes = [ui_to_db[c] for c in sel_color if c in ui_to_db]
        if selected_codes:
            pattern = '|'.join(selected_codes)
            df_f = df_f[df_f['color'].str.contains(pattern, na=False)]

    if df_f.empty:
        return None

    # 3. Summarize using your existing internal feature
    from features import summarize_by_cmc
    cmc_data = summarize_by_cmc(df_f)
    
    if cmc_data.empty:
        return None

    # 4. Sort and Plot
    cmc_data = cmc_data.sort_values(by='CMC', ascending=not is_transposed)
    
    if is_transposed:
        fig = px.bar(cmc_data, x='Count', y='CMC', orientation='h', text_auto=True, custom_data=['Value'])
        fig.update_layout(yaxis=dict(type='category', title="CMC"))
        h_template = "<b>CMC %{y}</b><br>Qty: %{x}<br>Value: $%{customdata[0]:,.2f}<extra></extra>"
    else:
        fig = px.bar(cmc_data, x='CMC', y='Count', text_auto=True, custom_data=['Value'])
        fig.update_layout(xaxis=dict(tickmode='linear', dtick=1, title="CMC"))
        h_template = "<b>CMC %{x}</b><br>Qty: %{y}<br>Value: $%{customdata[0]:,.2f}<extra></extra>"

    fig.update_traces(
        marker_color=METALLIC_GRAY, 
        hovertemplate=h_template
    )
    
    fig.update_layout(
        height=400, 
        margin=dict(l=20, r=20, t=10, b=10), 
        paper_bgcolor='rgba(0,0,0,0)', 
        plot_bgcolor='rgba(0,0,0,0)'
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
def summarize_color_identity(df_all_decks, df_battle_box, section):
    
    # 1. Identity based ONLY on the filtered section (e.g., 'main')
    def get_identity(mana_series):
        colors = set()
        all_mana = "".join(mana_series.dropna().astype(str))
        for char in "WUBRG":
            if char in all_mana: colors.add(char)
        if not colors: return "Colorless"
        if len(colors) >= 4: return "4+ Colors"
        return utility_maps.COLOR_NAME_MAP.get(frozenset(colors), "Unknown")

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
