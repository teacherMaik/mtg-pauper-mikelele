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

# Cache Aggregate data
@st.cache_data
def get_top_sets_aggregate(df):
    """Aggregate set data for top 12 sets. Cache only depends on DF, not sort_metric."""
    set_data = df.groupby('edition').agg(
        qty=('qty', 'sum'),
        total_cards_value=('total_cards_value', 'sum')
    ).reset_index()
    return set_data


def get_top_sets_donut(set_data, sort_metric):
    """Render donut chart from aggregated set data. Not cached."""
    
    if set_data.empty:
        return None

    col_key = 'qty' if sort_metric == "Qty" else 'total_cards_value'
    set_data_sorted = set_data.sort_values(by=col_key, ascending=False).head(12)

    metallic_rgba = [
        'rgba(44, 62, 80, 1.0)', 'rgba(44, 62, 80, 0.9)', 'rgba(44, 62, 80, 0.8)',
        'rgba(44, 62, 80, 0.7)', 'rgba(44, 62, 80, 0.6)', 'rgba(44, 62, 80, 0.5)',
        'rgba(44, 62, 80, 0.45)', 'rgba(44, 62, 80, 0.4)', 'rgba(44, 62, 80, 0.35)',
        'rgba(44, 62, 80, 0.3)', 'rgba(44, 62, 80, 0.25)', 'rgba(44, 62, 80, 0.2)'
    ]

    fig = px.pie(
        set_data_sorted, 
        values=col_key, 
        names='edition', 
        hole=0.42, 
        color_discrete_sequence=metallic_rgba
    )

    hover_template = "<b>%{label}</b><br>Qty: %{value}<extra></extra>" if sort_metric == "Qty" \
             else "<b>%{label}</b><br>Value: $%{value:.2f}<extra></extra>"

    fig.update_traces(
        hovertemplate=hover_template,
        marker=dict(line=dict(color='white', width=1)),
        textinfo='percent'
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


@st.cache_data
def get_color_saturation_aggregate(df):
    """Aggregate color distribution. No parameters — caller filters DF before passing."""
    df_colors = df[df['color'] != 'L'].copy()
    grand_total_qty = df_colors['qty'].sum()
    return df_colors, grand_total_qty


@st.cache_data
def get_land_mana_saturation_agg(df):
    """
    Caches the filtered land data.
    Directly uses 'land_mana' as the production identity.
    """
    if df.empty:
        return pd.DataFrame(), 0
        
    # 1. Filter for Lands only
    land_df = df[df['color'] == 'L'].copy()
    
    # 2. Point 'color' to 'land_mana' for the widget's logic
    # We fillna('C') just in case a land has no production data (like Evolving Wilds)
    land_df['color'] = land_df['land_mana'].fillna('C').astype(str)
    
    # 3. Boolean flag: True if it produces > 1 color
    # This is used by the widget to split mono vs multi segments
    land_df['is_multi_colored'] = land_df['color'].str.len() > 1
    
    grand_total = land_df['qty'].sum()
    
    return land_df, grand_total


def get_color_saturation_widget(df_colors, grand_total_qty, is_transposed):
    """Render stacked bar chart from aggregated color data. Not cached."""
    
    if df_colors.empty:
        return None

    fig = go.Figure()
    bar_orient = 'h' if is_transposed else 'v'

    colors_map = {
        'W': '#F0F2F0', 'U': '#0E68AB', 'B': '#150B00',
        'R': '#D3202A', 'G': '#00733E', 'C': LIGHT_GRAY, 'Multi': POP_GOLD
    }

    categories = [
        ('W','White'), ('U','Blue'), ('B','Black'),
        ('R','Red'), ('G','Green'), ('C','Colorless'), ('Multi','Multicolor')
    ]
    
    for code, name in categories:
        if code in 'WUBRG':
            df_mono_colored = df_colors[(df_colors['color'] == code) & (df_colors['is_multi_colored'] == False)]
            df_mutli_colored = df_colors[(df_colors['color'].str.contains(code, na=False)) & (df_colors['is_multi_colored'] == True)]
        elif code == 'C':
            df_mono_colored = df_colors[df_colors['color'] == 'C']
            df_mutli_colored = df_colors.iloc[0:0]
        else:
            df_mono_colored = df_colors.iloc[0:0]
            df_mutli_colored = df_colors[df_colors['is_multi_colored'] == True]

        qty_mono, qty_multi = df_mono_colored['qty'].sum(), df_mutli_colored['qty'].sum()
        value_mono = df_mono_colored['total_cards_value'].sum() if 'total_cards_value' in df_mono_colored.columns else 0
        value_multi = df_mutli_colored['total_cards_value'].sum() if 'total_cards_value' in df_mutli_colored.columns else 0
        
        total_present_val = value_mono + value_multi
        total_present_qty = qty_mono + qty_multi
        collection_percent = (total_present_qty / grand_total_qty * 100) if grand_total_qty > 0 else 0
        remainder_qty = grand_total_qty - total_present_qty

        def add_seg(s_name, val, col, hover_template):
            if val <= 0: return
            x_v, y_v = ([val], [name]) if is_transposed else ([name], [val])
            fig.add_trace(go.Bar(
                name=s_name, x=x_v, y=y_v, orientation=bar_orient,
                marker=dict(color=col, line=dict(color=BORDER_COLOR, width=1.5)),
                hovertemplate=hover_template, showlegend=False))
            
        add_seg(name, qty_mono, colors_map[code],
                f"<b>{name}</b><br>Qty: {qty_mono}<br>Value: ${value_mono:,.2f}<extra></extra>")
        
        add_seg("Multi", qty_multi, POP_GOLD,
                f"<b>Multi</b><br>Qty: +{qty_multi}<br>Value: +${value_multi:,.2f}<extra></extra>")
        
        add_seg("Remainder", remainder_qty, METALLIC_GRAY,
                f"<b>{name} Pips</b><br>% of Cards: {collection_percent:.1f}%<br>Total Value: ${total_present_val:,.2f}<extra></extra>")

    fig.update_layout(
        barmode='stack',
        height=550 if not is_transposed else 450,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=10, b=50, l=10, r=10)
    )

    if is_transposed:
        fig.update_yaxes(autorange="reversed")

    return fig


@st.cache_data
def get_type_distribution_aggregate(df):
    """Aggregate card type distribution. Caller filters DF before passing."""
    
    if df.empty:
        return pd.DataFrame()

    valid_types = [
        'Creature', 'Instant', 'Sorcery', 'Artifact',
        'Enchantment', 'Planeswalker', 'Land', 'Battle'
    ]

    rows = []
    for card_type in valid_types:
        subset = df[df['type'].str.contains(card_type, na=False, case=False)]
        if not subset.empty:
            rows.append({
                'Type': card_type,
                'Count': int(subset['qty'].sum()),
                'Value': subset['total_cards_value'].sum()
            })

    return pd.DataFrame(rows)


def get_type_distribution_widget(type_data):
    """Render donut chart from aggregated type data. Not cached."""
    
    if type_data.empty:
        return None
    
    metallic_rgba = [
        'rgba(44, 62, 80, 1.0)', 'rgba(44, 62, 80, 0.9)',
        'rgba(44, 62, 80, 0.8)', 'rgba(44, 62, 80, 0.7)',
        'rgba(44, 62, 80, 0.6)', 'rgba(44, 62, 80, 0.5)',
        'rgba(44, 62, 80, 0.4)', 'rgba(44, 62, 80, 0.3)',
        'rgba(44, 62, 80, 0.2)', 'rgba(44, 62, 80, 0.1)'
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


@st.cache_data
def get_mana_curve_aggregate(df):
    """Aggregate mana curve. Caller filters by type/color/section first."""
    
    if df is None or df.empty:
        return pd.DataFrame()

    df_cmc = df[df['primary_type_for_deck'] != 'Land'].copy()

    if df_cmc.empty:
        return pd.DataFrame()

    # Add chart labels
    df_cmc['chart_label'] = df_cmc.apply(lambda x: 'X' if x['cmc_has_x'] else str(int(x['cmc'])), axis=1)
    df_cmc['chart_sort'] = df_cmc.apply(lambda x: 99 if x['cmc_has_x'] else int(x['cmc']), axis=1)

    # Always aggregate names for hover
    curve_data = df_cmc.groupby(['chart_label', 'chart_sort']).agg({
        'qty': 'sum',
        'total_cards_value': 'sum',
        'name': lambda x: "<br>".join([f"• {n}" for n in sorted(x.unique())])
    }).reset_index()
    
    return curve_data


def get_mana_curve_widget(curve_data, page_view, is_transposed):
    """Render mana curve from aggregated data. Not cached."""
    
    if curve_data.empty:
        return None

    curve_data_sorted = curve_data.sort_values('chart_sort', ascending=not is_transposed)

    METALLIC_GRAY = '#2c3e50' 
    x_col, y_col = ('qty', 'chart_label') if is_transposed else ('chart_label', 'qty')
    
    fig = px.bar(
        curve_data_sorted, x=x_col, y=y_col, 
        orientation='h' if is_transposed else 'v',
        text_auto=True, 
        custom_data=['total_cards_value', 'name']
    )

    l_ref = "%{y}" if is_transposed else "%{x}"
    q_ref = "%{x}" if is_transposed else "%{y}"
    
    hover_tmpl = f"<b>CMC {l_ref}</b><br>Qty: {q_ref}"
    
    if page_view != 'Deck Test':
        hover_tmpl += f"<br>Value: $%{'{customdata[0]:,.2f}'}"
    
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
def get_top_12_staples_aggregate(df):
    """Aggregate top staples by card name. Caller filters DF before passing."""
    
    if df.empty:
        return pd.DataFrame()
    
    # Get deck column name
    deck_col = 'deck_name' if 'deck_name' in df.columns else 'DeckName'
    
    # Just group and aggregate
    top_cards = df.groupby('name').agg({
        'qty': 'sum',
        deck_col: 'nunique'
    }).reset_index()

    # Sort and limit to top 12
    top_12 = top_cards.sort_values(
        by=[deck_col, 'qty'], 
        ascending=[False, False]
    ).head(12).iloc[::-1]
    
    return top_12


def get_top_12_staples_widget(top_12_data, deck_col):
    """Render treemap from aggregated staples data. Not cached."""
    
    if top_12_data.empty:
        return None

    fig_heat = px.treemap(
        top_12_data,
        path=[px.Constant("Top Staples"), 'name'],
        values='qty',
        color=deck_col,
        color_continuous_scale=[[0, 'rgba(44, 62, 80, 0.2)'], [1, 'rgba(44, 62, 80, 1.0)']], 
        custom_data=['qty', deck_col]
    )
    
    fig_heat.update_traces(
        textinfo="label+value",
        textfont=dict(color='white', size=14),
        hovertemplate="<b>%{label}</b><br>Total Copies: %{customdata[0]}<br>In %{customdata[1]} Decks<extra></extra>"
    )
    
    fig_heat.update_layout(
        coloraxis_showscale=False,
        margin=dict(l=0, r=0, t=0, b=0),
        height=420
    )
    
    return fig_heat


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
        
        inventory, needed = subset['qty'].sum(), subset['num_for_deck'].sum()
        return int(inventory), int(needed), (needed / inventory * 100) if inventory > 0 else 0

    deck_completeness = df_all_decks.groupby('DeckName').apply(lambda x: (x['num_for_deck'] >= x['qty']).all())

    # Total Decks Row
    deck_names = df_battle_box['DeckName'].unique()

    total_inventory, total_needed, total_pct = calc_card_stats(deck_names)

    stats_list.append({"Cat": "Total", "nº": len(deck_names), "nº complete": int(deck_completeness.sum()), 
                       "cards": total_inventory, "cards collected": total_needed, "% cards": total_pct})

    for cat in categories:

        col = 'Archetype' if cat in ["Aggro", "Midrange", "Tempo", "Control", "Combo"] else 'Brew'

        deck_categories = df_battle_box[df_battle_box[col] == cat]['DeckName'].unique()

        deck_cat_inventory, deck_cat_needed, deck_cat_pct = calc_card_stats(deck_categories)

        deck_cat_complete = deck_completeness.reindex(deck_categories).fillna(False).sum()

        stats_list.append({"Cat": cat, "nº": len(deck_categories), "nº complete": int(deck_cat_complete), 
                           "cards": deck_cat_inventory, "cards collected": deck_cat_needed, "% cards": deck_cat_pct})

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
