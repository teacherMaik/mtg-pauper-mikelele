import streamlit as st
import pandas as pd
import features
import plotly.express as px

METALLIC_GRAY = "#2c3e50"

def render_row_1(df_all_decks, df_battle_box):

    df_main_stats = features.get_battle_box_stats(df_battle_box, df_all_decks, 'main')
    df_side_stats = features.get_battle_box_stats(df_battle_box, df_all_decks, 'sideboard')

    row_1_col_left, row_1_col_right = st.columns([1, 1], gap="large")
    
    # --- ROW 1: COMPOSITION ---
    with row_1_col_left:
        
        st.markdown("## Battle Box Stats")
    
        # Radio filter to switch context
        view_section = st.radio(
            "Section",
            ["Main", "Sideboard"],
            horizontal=True,
            label_visibility="collapsed",
            key="bb_stats_toggle"
        )

        # Fetch the appropriate data based on radio selection
        # (Using the logic from your get_battle_box_stats function)
        if view_section == "Main":
            display_df = df_main_stats
        else:
            display_df = df_side_stats

        # Apply your metallic gray theme to the "Decks" row
        styled_df = display_df.style.apply(
            lambda x: ['background-color: #34495e; color: white; font-weight: bold' 
                    if x['Cat'] == 'Decks' else '' for _ in x], axis=1
        )

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Cat": "Category",
                "nº": st.column_config.NumberColumn("Decks", format="%d"),
                "nº complete": st.column_config.NumberColumn("Complete", format="%d"),
                "cards": st.column_config.NumberColumn("Qty", format="%d"),
                "cards collected": st.column_config.NumberColumn("Collected", format="%d"),
                "% cards": st.column_config.ProgressColumn(
                    f"% {view_section}", 
                    format="%.1f%%", 
                    min_value=0, 
                    max_value=100
                )
            }
        )

    with row_1_col_right:
        with st.container(border=True):
            st.markdown("## Top 12 Staples")
            
            # --- TWO ROW RADIO FILTERS ---
            
            section_filter = st.radio("Section:", ["Main", "Sideboard"], horizontal=True, label_visibility="collapsed")
        
            # Archetype options
            archetype_filter = st.radio("Archetype:", ["All", "Aggro", "Midrange", "Tempo", "Control"], horizontal=True, label_visibility="collapsed")

            # 1. MERGE deck metadata to get Archetypes for the cards
            # We merge df_all_decks with df_battle_box on the deck name column
            deck_col = 'deck_name' if 'deck_name' in df_all_decks.columns else 'DeckName'
            df_with_meta = df_all_decks.merge(
                df_battle_box[[deck_col, 'Archetype']], 
                on=deck_col, 
                how='left'
            )

            # 2. APPLY BOTH FILTERS
            # Filter: No Lands + Section + (Archetype if not "All")
            mask = (
                (~df_with_meta['type'].str.contains('Land', case=False, na=False)) & 
                (df_with_meta['section'].str.lower() == section_filter.lower())
            )
            
            if archetype_filter != "All":
                mask = mask & (df_with_meta['Archetype'] == archetype_filter)

            df_filtered_staples = df_with_meta[mask].copy()
            
            # 3. AGGREGATE
            top_cards = df_filtered_staples.groupby('name').agg({'qty': 'sum', deck_col: 'nunique'}).reset_index()
            
            top_12 = top_cards.sort_values(
                by=[deck_col, 'qty'], 
                ascending=[False, False]
            ).head(12).iloc[::-1]

            if top_12.empty:
                st.info(f"No {archetype_filter} cards found in {section_filter}")
            else:
                # --- THE TREEMAP ---
                # Using your gradient instruction: metallic gray for the top staples
                fig_heat = px.treemap(
                    top_12,
                    path=[px.Constant("Top Staples"), 'name'],
                    values='qty',
                    color=deck_col,
                    # Metallic gray gradient as requested
                    color_continuous_scale=[[0, '#bdc3c7'], [1, '#34495e']], 
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
                    height=420 # Slightly reduced to account for double radio rows
                )
                
                st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})


def render_row_2(df_all_decks, df_battle_box):
    with st.container(border=True):
        # Header Row with Transpose Toggle
        col_head, col_empty, col_transpose = st.columns([2, 3, 1])
        
        with col_head:
            st.markdown("## Deck Colors (Main)")
        
        with col_transpose:
            is_transposed = st.toggle("Transpose", key="ident_transpose")

        # Fetch the data
        df_ident_stats = features.get_color_identity_stats(df_all_decks, df_battle_box, 'main')

        if is_transposed:
            # Transposing logic: Flip the dataframe and use 'Identity' as headers
            df_display = df_ident_stats.set_index('Identity').T.reset_index()
            # Rename the index column for clarity
            df_display.rename(columns={'index': 'Metric'}, inplace=True)
            
            st.dataframe(
                df_display,
                use_container_width=True,
                hide_index=True
            )
        else:
            # Standard View
            st.dataframe(
                df_ident_stats,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Identity": "MTG Identity",
                    "nº": st.column_config.NumberColumn("Decks", format="%d"),
                    "nº complete": st.column_config.NumberColumn("Complete", format="%d"),
                    "cards": st.column_config.NumberColumn("Main Qty", format="%d"),
                    "cards collected": st.column_config.NumberColumn("Main Collected", format="%d"),
                    "% cards": st.column_config.ProgressColumn(
                        "Overall %", 
                        format="%.1f%%", 
                        min_value=0, 
                        max_value=100
                    )
                }
            )


def render_row_3(df_all_decks):
    row_2_col_left, row_2_col_right = st.columns([1, 1], gap="large")

    with row_2_col_left:
        with st.container(border=True):
            st.markdown("## Cards By Colors")
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

            st.markdown("## Cards By Type")
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


def render_row_4(df_all_decks):

    with st.container(border=True):

        col_head, col_filter_1, col_filter_2, col_transpose = st.columns([1, 1.5, 1.5, 0.8])
        with col_head: 
            st.markdown("### Mana Curve")
        with col_filter_1:
            sel_type = st.multiselect("Filter by Type:", options=['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment'], key="cmc_t_f", label_visibility="collapsed")
        with col_filter_2:
            sel_color = st.multiselect("Filter by Color:", options=['White', 'Blue', 'Black', 'Red', 'Green', 'Colorless'], key="cmc_c_f", label_visibility="collapsed")
        with col_transpose:
            is_transposed = st.toggle("Transpose", key="cmc_transpose")

        # 1. Apply Filtering
        df_cmc = df_all_decks.copy()
        
        if sel_type:
            df_cmc = df_cmc[df_cmc['type'].str.contains('|'.join(sel_type), case=False, na=False)]
            
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
                df_cmc = df_cmc[df_cmc['color'].str.contains(pattern, na=False)]

        # 2. Check for empty results AFTER filtering
        filters_active = any([sel_type, sel_color])

        if df_cmc.empty and filters_active:
            st.write("") 
            st.info("Mikelele has no such cards...")
            st.write("")
        else:
            # 3. Get Stats and Render Chart
            _, _, cmc_data = features.get_stats(df_cmc)
            
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


def render_bb_stats_view(df_all_decks, df_battle_box):
    # Pass df_all_decks and df_all_decks to your existing render_row_1 logic
    render_row_1(df_all_decks, df_battle_box) 
    render_row_2(df_all_decks, df_battle_box)
    st.divider()
    render_row_3(df_all_decks)
    render_row_4(df_all_decks)