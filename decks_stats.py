import streamlit as st
import pandas as pd
import features
import plotly.express as px

METALLIC_GRAY = "#2c3e50"

def render_row_1(df_all_decks):
    # --- 1. Aggregation for Left Column Tables ---
    rarity_stats = features.get_rarity_stats(df_all_decks).rename(
        columns={'rarity': 'Stat', 'qty': 'Count', 'total_cards_value': 'Value'}
    )
    
    total_qty = df_all_decks['qty'].sum()
    total_val = df_all_decks['total_cards_value'].sum()
    
    summary_data = pd.DataFrame([{
        'Stat': 'Total Cards',
        'Count': total_qty,
        'Value': total_val,
        'Usage_Pct': 100.0,
        'In_Decks_Qty': total_qty,
        'In_Decks_Val': total_val
    }])
    
    rarity_stats['In_Decks_Qty'] = rarity_stats['Count']
    rarity_stats['In_Decks_Val'] = rarity_stats['Value']
    rarity_stats['Usage_Pct'] = 100.0
    
    rarity_sorted = rarity_stats.sort_values(by='Count', ascending=False)
    full_rarity_df = pd.concat([summary_data, rarity_sorted], ignore_index=True)

    land_data = features.get_land_breakdown(df_all_decks)
    land_data['In_Decks_Qty'] = land_data['Count']
    land_data['In_Decks_Val'] = land_data['Value']
    land_data['Usage_Pct'] = 100.0

    # --- 3. UI Layout ---
    c1, c2 = st.columns([1, 1], gap="large")
    
    with c1:
        st.markdown("## Composition")
        shared_config = {
            "Stat": st.column_config.TextColumn(" ", width=120),
            "Count": st.column_config.NumberColumn("Qty", format="%d", width=60),
            "Value": st.column_config.NumberColumn("Value", format="$%.2f", width=80),
            "Usage_Pct": st.column_config.ProgressColumn("% in Decks", format="%.1f%%", min_value=0, max_value=100, width=100),
            "In_Decks_Qty": st.column_config.NumberColumn("Qty in Decks", format="%d", width=80),
            "In_Decks_Val": st.column_config.NumberColumn("Value in Decks", format="$%.2f", width=100)
        }

        st.dataframe(
            full_rarity_df.style.apply(lambda s: [f'background-color: {METALLIC_GRAY}; color: white;' if s.name == 0 else '' for _ in s], axis=1),
            use_container_width=True, hide_index=True, column_config=shared_config
        )
        
        st.dataframe(
            land_data, use_container_width=True, hide_index=True, 
            column_order=("Stat", "Count", "Value", "Usage_Pct", "In_Decks_Qty", "In_Decks_Val"),
            column_config=shared_config
        )

    with c2:
        with st.container(border=True):
            st.markdown("## Top 12 Staples")
            
            # --- RADIO FILTER ---
            section_f = st.radio("Section:", ["Main", "Sideboard"], horizontal=True, label_visibility="collapsed")

            # --- Aggregation for Right Column (Filtered by Radio + No Lands) ---
            df_no_lands = df_all_decks[
                (~df_all_decks['type'].str.contains('Land', case=False, na=False)) & 
                (df_all_decks['section'].str.lower() == section_f.lower())
            ].copy()
            
            deck_col = 'deck_name' if 'deck_name' in df_no_lands.columns else 'DeckName'
            top_cards = df_no_lands.groupby('name').agg({'qty': 'sum', deck_col: 'nunique'}).reset_index()
            
            # 3. FIX: MULTI-LEVEL SORT (Decks first, then Qty)
            # We sort descending for both to get the real staples at the top
            top_12 = top_cards.sort_values(
                by=[deck_col, 'qty'], 
                ascending=[False, False]
            ).head(12).iloc[::-1] # Reverse for Plotly horizontal bars

            if top_12.empty:
                st.info(f"No cards found in {section_f}")
            else:
                # --- THE HEATMAP (TREEMAP) ---
                fig_heat = px.treemap(
                    top_12,
                    path=[px.Constant("Top Staples"), 'name'], # Hierarchy: Root -> Card Name
                    values='qty',       # Box SIZE = total copies
                    color=deck_col,     # Box COLOR = number of decks
                    color_continuous_scale=[[0, '#bdc3c7'], [1, METALLIC_GRAY]],
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
                    height=450
                )
                
                st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})

        
def render_row_2(df_all_decks):
    row_2_col_left, row_2_col_right = st.columns([1, 1], gap="large")

    with row_2_col_left:
        with st.container(border=True):
            st.markdown("### Collection By Color")
            # Filter Pie by Rarity
            all_rarities = df_all_decks['rarity'].unique()
            sel_rarity = st.multiselect("Filter Pie by Rarity:", options=all_rarities, key="color_rarity_filter")
            
            df_p = df_all_decks[df_all_decks['rarity'].isin(sel_rarity)] if sel_rarity else df_all_decks
            
            # Message logic for Rarity Filter
            if df_p.empty and sel_rarity:
                st.write("")
                st.info("Mikelele has no such cards...")
                st.write("")
            else:
                color_data, _, _ = features.get_stats(df_p)

                if not color_data.empty:
                    color_map = {
                        'White': '#F0F0F0', 'Blue': '#0000FF', 'Black': '#000000', 
                        'Red': '#FF0000', 'Green': '#008000', 'Colorless': '#90ADBB', 'Land': "#6D5025"
                    }
                    fig_pie = px.pie(color_data, values='Count', names='Color', color='Color', color_discrete_map=color_map, hole=0.4)
                    fig_pie.update_traces(
                        customdata=color_data['Value'], 
                        hovertemplate="<b>%{label}</b><br>Qty: %{value}<br>Value: $%{customdata:,.2f}<extra></extra>", 
                        textinfo='none', 
                        marker=dict(line=dict(color='#444444', width=1.5))
                    )
                    fig_pie.update_layout(showlegend=True, height=350, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

    with row_2_col_right:
        with st.container(border=True):
            st.markdown("### Collection By Type")
            # Multiselect options
            sel_color = st.multiselect("Filter by Color:", options=['White', 'Blue', 'Black', 'Red', 'Green', 'Colorless'], key="typ_f")
            
            df_b = df_all_decks.copy()
            if sel_color:
                # Map UI names to DB codes
                ui_to_db = {
                    'White': 'W', 'Blue': 'U', 'Black': 'B', 
                    'Red': 'R', 'Green': 'G', 'Colorless': 'C'
                }
                selected_codes = [ui_to_db[c] for c in sel_color if c in ui_to_db]
                
                if selected_codes:
                    # Functional identity: {W}{B} or {WB} matches both White and Black filters
                    pattern = '|'.join(selected_codes)
                    df_b = df_b[df_b['color'].str.contains(pattern, na=False)]
            
            # Message logic for Color Filter
            if df_b.empty and sel_color:
                st.write("")
                st.info("Mikelele has no such cards...")
                st.write("")
            else:
                _, type_data, _ = features.get_stats(df_b)

                if not type_data.empty:
                    # Sort ascending for highest count at top of horizontal chart
                    type_data = type_data.sort_values(by='Count', ascending=True)

                    fig_bar = px.bar(
                        type_data, 
                        x='Count', 
                        y='Type', 
                        orientation='h', 
                        text='Count', 
                        custom_data=['Value'], 
                        color_discrete_sequence=[METALLIC_GRAY]
                    )
                    
                    fig_bar.update_traces(
                        textposition='inside', 
                        textfont=dict(color='white'), 
                        hovertemplate="<b>%{y}</b><br>Qty: %{x}<br>Total Value: $%{customdata[0]:,.2f}<extra></extra>"
                    )
                    
                    fig_bar.update_layout(
                        showlegend=False, 
                        height=350, 
                        margin=dict(l=10, r=10, t=10, b=10), 
                        xaxis_title=None, 
                        yaxis_title=None,
                        yaxis={'categoryorder': 'trace'} # Respect dataframe sort
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)


def render_row_3(df_all_decks):
    with st.container(border=True):
        c_head, c_f1, c_f2, c_f3 = st.columns([1, 1.5, 1.5, 0.8])
        with c_head: 
            st.markdown("### Mana Curve")
        with c_f1:
            sel_type = st.multiselect("Filter by Type:", options=['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment'], key="cmc_t_f", label_visibility="collapsed")
        with c_f2:
            sel_color = st.multiselect("Filter by Color:", options=['White', 'Blue', 'Black', 'Red', 'Green', 'Colorless'], key="cmc_c_f", label_visibility="collapsed")
        with c_f3:
            is_transposed = st.toggle("Transpose", key="cmc_transpose")

        # 1. Apply Filtering
        df_c = df_all_decks.copy()
        
        if sel_type:
            df_c = df_c[df_c['type'].str.contains('|'.join(sel_type), case=False, na=False)]
            
        if sel_color:
            # Map UI to DB Codes
            ui_to_db = {
                'White': 'W', 'Blue': 'U', 'Black': 'B', 
                'Red': 'R', 'Green': 'G', 'Colorless': 'C'
            }
            selected_codes = [ui_to_db[c] for c in sel_color if c in ui_to_db]
            
            if selected_codes:
                # Regex 'OR' check: a {W}{B} or {WB} card matches if 'White' OR 'Black' is selected
                pattern = '|'.join(selected_codes)
                df_c = df_c[df_c['color'].str.contains(pattern, na=False)]

        # 2. Check for empty results AFTER filtering
        filters_active = any([sel_type, sel_color])

        if df_c.empty and filters_active:
            st.write("") 
            st.info("Mikelele has no such cards...")
            st.write("")
        else:
            # 3. Get Stats and Render Chart
            _, _, cmc_data = features.get_stats(df_c)
            
            if not cmc_data.empty:
                # Ensure CMC is treated as a category for proper discrete axis spacing
                cmc_data = cmc_data.sort_values(by='CMC', ascending=not is_transposed)
                
                if is_transposed:
                    fig_cmc = px.bar(cmc_data, x='Count', y='CMC', orientation='h', text_auto=True, custom_data=['Value'])
                    fig_cmc.update_layout(yaxis=dict(type='category', title="CMC"))
                    # Hover adjustment for horizontal mode
                    h_template = "<b>CMC %{y}</b><br>Qty: %{x}<br>Value: $%{customdata[0]:,.2f}<extra></extra>"
                else:
                    fig_cmc = px.bar(cmc_data, x='CMC', y='Count', text_auto=True, custom_data=['Value'])
                    fig_cmc.update_layout(xaxis=dict(tickmode='linear', dtick=1, title="CMC"))
                    h_template = "<b>CMC %{x}</b><br>Qty: %{y}<br>Value: $%{customdata[0]:,.2f}<extra></extra>"

                fig_cmc.update_traces(
                    marker_color=METALLIC_GRAY, 
                    hovertemplate=h_template
                )
                
                fig_cmc.update_layout(
                    height=400, 
                    margin=dict(l=20, r=20, t=10, b=10), 
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_cmc, use_container_width=True, config={'displayModeBar': False})


def render_bb_stats_view(df_all_decks):
    # Pass df_all_decks and df_all_decks to your existing render_row_1 logic
    render_row_1(df_all_decks) 
    render_row_2(df_all_decks)
    st.divider()
    render_row_3(df_all_decks)