import streamlit as st
import pandas as pd
import features
import plotly.express as px
import plotly.graph_objects as go

METALLIC_GRAY = "#2c3e50"

def render_row_1(df_all_decks, df_battle_box):

    df_main_stats = features.summarize_battle_box(df_battle_box, df_all_decks, 'main')
    df_side_stats = features.summarize_battle_box(df_battle_box, df_all_decks, 'sideboard')

    row_1_col_left, row_1_col_right = st.columns([1, 1], gap="small")
    
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
            
            section_filter = st.radio("Section:", ["Main", "Sideboard"], horizontal=True, label_visibility="collapsed")
            archetype_filter = st.radio("Archetype:", ["All", "Aggro", "Midrange", "Tempo", "Control", "Combo"], horizontal=True, label_visibility="collapsed")

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
                    height=420 # Slightly reduced to account for double radio rows
                )
                
                st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})


def render_row_2(df_all_decks, df_battle_box):

    with st.container(border=True):
        # 1. Header and Archetype Filter
        st.markdown("## Deck Colors (Main)")
        
        archetypes = ["All", "Aggro", "Midrange", "Tempo", "Control", "Combo"]
        selected_arch = st.radio(
            "Filter by Archetype", 
            options=archetypes, 
            horizontal=True, 
            key="stats_arch_filter"
        )

        # 2. Filter the Battle Box dataframe based on selection
        # This ensures the stats only count decks within the chosen archetype
        df_filtered_bb = df_battle_box.copy()

        if selected_arch != "All":
            if 'Archetype' in df_filtered_bb.columns:
                df_filtered_bb = df_filtered_bb[df_filtered_bb['Archetype'] == selected_arch]
            else:
                st.warning("Archetype column not found in data.")

        # 3. Fetch the data using the filtered Battle Box
        df_ident_stats = features.summarize_color_identity(df_all_decks, df_filtered_bb, 'main')

        # 4. Standard View Rendering (Transpose removed)
        if df_ident_stats.empty:
            st.info(f"No data available for archetype: {selected_arch}")
        else:
            st.dataframe(
                df_ident_stats,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Identity": "Identity",
                    "nº": st.column_config.NumberColumn("Nº Decks", format="%d"),
                    "nº complete": st.column_config.NumberColumn("Nº Complete", format="%d"),
                    "cards": st.column_config.NumberColumn("Total Cards", format="%d"),
                    "cards collected": st.column_config.NumberColumn("Cards Collected", format="%d"),
                    "% cards": st.column_config.ProgressColumn(
                        "% Cards Collected", 
                        format="%.1f%%", 
                        min_value=0, 
                        max_value=100
                    )
                }
            )


def render_row_3(df_all_decks):

    row_2_col_left, row_2_col_right = st.columns([1, 1], gap="small")

    with row_2_col_left:
        with st.container(border=True):
            # Custom Header
            st.markdown(f'''
                <div style="display: flex; justify-content: flex-start; align-items: flex-end; flex-wrap: wrap; margin-bottom: 10px;">
                    <h3 style="margin: 0; padding-bottom: 0">Cards by Colors</h3>
                    <p style="padding-bottom: 0; margin-bottom: 0; margin-left: 10px;">
                        <em style="font-size: 0.85rem; color: #888;">*Lands Excluded</em>
                    </p>
                </div>
            ''', unsafe_allow_html=True)
            
            is_trans = st.toggle("Transpose", key="inv_trans")

            filter_col_left, filter_col_right = st.columns(2)

            with filter_col_left:
                rarity_select = st.multiselect("Filter Rarity:", ['Common', 'Uncommon', 'Rare', 'Mythic'], key="inv_rarity")
            with filter_col_right:
                count_select = st.radio("Count Mode:", ["All", "Unique"], horizontal=True, key="inv_view")

            # Calling the single refactored function
            fig_colors = features.get_color_saturation_widget(
                df_all_decks,
                is_trans,
                rarity_select,
                count_select=count_select
            )
            if fig_colors:
                st.plotly_chart(fig_colors, use_container_width=True, key="inv_color_plot")
            else:
                st.info("No cards found for this selection.")

    with row_2_col_right:

        with st.container(border=True):
            # Custom Header
            st.markdown('<h3 style="margin: 0; margin-bottom: 10px;">Cards By Type</h3>', unsafe_allow_html=True)
            
            # --- INVENTORY VIEW CALL ---
            filter_col_left, filter_col_right = st.columns(2)

            with filter_col_left:
                # Inventory usually shows all possible colors
                color_options = ['White', 'Blue', 'Black', 'Red', 'Green', 'Colorless', 'Multicolor']
                color_select = st.multiselect("Filter Color:", color_options, key="inv_type_col")

            with filter_col_right:
                # Inventory needs the toggle for Unique cards vs Total Qty
                count_select = st.radio("Count Mode:", ["All", "Unique"], horizontal=True, key="inv_type_view")

            # The call passes count_select. is_deck remains None (default).
            fig_types = features.get_type_distribution_widget(
                df_all_decks, 
                color_select, 
                count_select=count_select
            )

            if fig_types:
                st.plotly_chart(fig_types, use_container_width=True, key="inv_type_plot")
            else:
                st.info("No cards found in your inventory for this selection.")


def render_row_4(df_all_decks):

    with st.container(border=True):
        
        c_head, c_f1, c_f2, c_f3 = st.columns([1, 1.5, 1.5, 0.8])
        with c_head: 
            st.markdown("### Mana Curve")
        with c_f1:
            sel_type = st.multiselect("Filter by Type:", options=['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment'], key="cmc_t_f", label_visibility="collapsed")
        with c_f2:
            sel_color = st.multiselect("Filter by Color:", options=['White', 'Blue', 'Black', 'Red', 'Green', 'Colorless'], key="cmc_c_f", label_visibility="collapsed")
        with c_f3:
            is_cmc_transposed = st.toggle("Transpose", key="cmc_transpose")

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
            cmc_data = features.summarize_by_cmc(df_c)
            
            if not cmc_data.empty:
                # Ensure CMC is treated as a category for proper discrete axis spacing
                cmc_data = cmc_data.sort_values(by='CMC', ascending=not is_cmc_transposed)
                
                if is_cmc_transposed:
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