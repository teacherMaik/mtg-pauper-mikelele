import streamlit as st
import pandas as pd
import plotly.express as px
import features

# Consistent styling constants
METALLIC_GRAY = "#2c3e50"
PRIMARY_RED = "#FF4B4B"

def render_deck_full_view(df_all_decks):
    """Entry point for the Deck-Only Analytics page"""
    st.title("Deck Analytics")
    
    # ROW 1: Rarity, Lands, and Set Distribution
    render_deck_row_1(df_all_decks)
    
    st.markdown("---")
    
    # ROW 2: Color and Type Distribution
    render_deck_row_2(df_all_decks)
    
    st.markdown("---")
    
    # ROW 3: Mana Curve
    render_deck_row_3(df_all_decks)

def render_deck_row_1(df_all_decks):
    # Data Processing
    rarity_data = features.get_rarity_stats(df_all_decks).rename(columns={'Rarity': 'Stat'})
    land_data = features.get_land_breakdown(df_all_decks)
    
    summary_data = pd.DataFrame([{
        'Stat': 'Total Deck Cards',
        'Count': df_all_decks['Qty'].sum(),
        'Value': df_all_decks['Total'].sum()
    }])
    full_rarity_df = pd.concat([summary_data, rarity_data], ignore_index=True)

    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        st.markdown("### Deck Composition")
        # Rarity Table
        st.dataframe(
            full_rarity_df.style.apply(lambda s: [f'background-color: {METALLIC_GRAY}; color: white;' if s.name == 0 else '' for _ in s], axis=1),
            use_container_width=True, hide_index=True,
            column_config={
                "Stat": "Category",
                "Count": st.column_config.NumberColumn("Qty", format="%d"),
                "Value": st.column_config.NumberColumn("Value", format="$%.2f"),
            }
        ).sort_values(by="Count", ascending=False)
        # Land Table
        st.dataframe(
            land_data, use_container_width=True, hide_index=True,
            column_config={
                "Stat": "", 
                "Count": st.column_config.NumberColumn("", format="%d"),
                "Value": st.column_config.NumberColumn("", format="$%.2f"),
            }
        ).sort_values(by="Count", ascending=False)

    with col_right:
        with st.container(border=True):
            st.markdown("### Top 12 Sets in Decks")
            set_data = features.get_set_stats(df_all_decks)
            top_sets = set_data.sort_values(by="Count", ascending=False).head(12)
            fig = px.pie(top_sets, values="Count", names='Edition', hole=0.4, 
                         color_discrete_sequence=px.colors.sequential.Blues_r)
            fig.update_layout(showlegend=True, height=400, margin=dict(l=10, r=10, t=10, b=10), 
                              legend=dict(orientation="h", y=-0.2))
            st.plotly_chart(fig, use_container_width=True)

def render_deck_row_2(df_all_decks):
    col_left, col_right = st.columns([1, 1], gap="large")

    with col_left:
        with st.container(border=True):
            st.markdown("### Deck Color Identity")
            color_data, _, _ = features.get_stats(df_all_decks)
            color_map = {'White': '#F0F0F0', 'Blue': '#0000FF', 'Black': '#000000', 'Red': '#FF0000', 'Green': '#008000', 'Colorless': '#90ADBB', 'Land': "#6D5025"}
            fig_pie = px.pie(color_data, values='Count', names='Color', color='Color', color_discrete_map=color_map, hole=0.4)
            fig_pie.update_layout(showlegend=True, height=350)
            st.plotly_chart(fig_pie, use_container_width=True)

    with col_right:
        with st.container(border=True):
            st.markdown("### Deck Card Types")
            # Filter UI
            sel_color = st.multiselect("Filter by Color:", options=['White', 'Blue', 'Black', 'Red', 'Green', 'Colorless'], key="deck_typ_f")
            
            df_bar = df_all_decks.copy()
            if sel_color:
                mana_series = df_bar['Mana'].fillna('')
                if "Colorless" in sel_color:
                    mask = ~mana_series.str.contains(r'[WUBRG]', case=False)
                    df_bar = df_bar[mask]
                else:
                    color_map = {'White':'W', 'Blue':'U', 'Black':'B', 'Red':'R', 'Green':'G'}
                    codes = [color_map[c] for c in sel_color if c in color_map]
                    df_bar = df_bar[mana_series.str.contains('|'.join(codes), case=False)]

            _, type_data, _ = features.get_stats(df_bar)
            fig_type = px.bar(type_data, x='Count', y='Type', orientation='h', text='Count', custom_data=['Value'])
            fig_type.update_traces(marker_color=PRIMARY_RED, textposition='inside', textfont=dict(color='white'),
                                   hovertemplate="<b>%{y}</b><br>Qty: %{x}<br>Value: $%{customdata[0]:,.2f}<extra></extra>")
            fig_type.update_layout(showlegend=False, height=300, margin=dict(l=10, r=10, t=10, b=10), xaxis_title=None, yaxis_title=None)
            st.plotly_chart(fig_type, use_container_width=True)

def render_deck_row_3(df_all_decks):
    with st.container(border=True):
        c_head, c_f1, c_f2, c_f3 = st.columns([1, 1.5, 1.5, 0.8])
        with c_head: st.markdown("### Deck Mana Curve")
        with c_f1: sel_type = st.multiselect("Types", options=['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment'], key="deck_cmc_t", label_visibility="collapsed")
        with c_f2: sel_color = st.multiselect("Colors", options=['White', 'Blue', 'Black', 'Red', 'Green', 'Colorless'], key="deck_cmc_c", label_visibility="collapsed")
        with c_f3: is_transposed = st.toggle("Flip", key="deck_cmc_flip")

        # Filtering logic
        df_filtered = df_all_decks.copy()
        if sel_type: df_filtered = df_filtered[df_filtered['Type'].str.contains('|'.join(sel_type), case=False, na=False)]
        if sel_color:
            mana_series = df_filtered['Mana'].fillna('')
            if "Colorless" in sel_color:
                df_filtered = df_filtered[~mana_series.str.contains(r'[WUBRG]', case=False)]
            else:
                color_map = {'White':'W', 'Blue':'U', 'Black':'B', 'Red':'R', 'Green':'G'}
                codes = [color_map[c] for c in sel_color if c in color_map]
                df_filtered = df_filtered[mana_series.str.contains('|'.join(codes), case=False)]

        _, _, cmc_data = features.get_stats(df_filtered)
        if not cmc_data.empty:
            cmc_data = cmc_data.sort_values(by='CMC', ascending=not is_transposed)
            if is_transposed:
                fig = px.bar(cmc_data, x='Count', y='CMC', orientation='h', text='Count', custom_data=['Value'])
                hover = "<b>CMC %{y}</b><br>Qty: %{x}<br>Value: $%{customdata[0]:,.2f}<extra></extra>"
            else:
                fig = px.bar(cmc_data, x='CMC', y='Count', text='Count', custom_data=['Value'])
                hover = "<b>CMC %{x}</b><br>Qty: %{y}<br>Value: $%{customdata[0]:,.2f}<extra></extra>"
            
            fig.update_traces(marker_color=PRIMARY_RED, textposition='inside', textfont=dict(color='white'), hovertemplate=hover)
            fig.update_layout(height=400, xaxis_title=None, yaxis_title=None, yaxis=dict(type='category') if is_transposed else dict(dtick=1))
            st.plotly_chart(fig, use_container_width=True)