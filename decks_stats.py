import streamlit as st
import pandas as pd
import features
import plotly.express as px
import plotly.graph_objects as go

METALLIC_GRAY = "#2c3e50"

def render_row_1(df_all_decks, df_battle_box):

    row_1_col_left, row_1_col_right = st.columns([1, 1], gap="small")
    
    # Comparative Tables Widget
    with row_1_col_left:
        
        st.markdown(f"## Battle Box Stats")
        # Radio Filters Main/Side
        view_section = st.radio(
            "Section", ["Main", "Sideboard"],
            horizontal=True, label_visibility="collapsed", key="bb_stats_toggle"
        )
        pct_col = 'CompletionPct' if view_section == "Main" else 'SideboardPct'

        # Build the Summary Tables
        def get_stats(df, group_col, label):
            # We define 'Complete' as having 100% in the chosen pct_col
            stats = df.groupby(group_col).agg({
                'DeckName': 'count',
                pct_col: lambda x: (x == 100).sum() # Count of 100% complete decks
            }).reset_index()
            
            # Add the average completion percentage
            avg_pct = df.groupby(group_col)[pct_col].mean().reset_index()
            stats = stats.merge(avg_pct, on=group_col)
            
            stats.columns = ['Cat', 'nº', 'nº complete', '% cards']
            return stats

        # First Row -> Overall
        overall_row = pd.DataFrame([{
            "Cat": "OVERALL", 
            "nº": len(df_battle_box),
            "nº complete": len(df_battle_box[df_battle_box[pct_col] == 100]),
            "% cards": df_battle_box[pct_col].mean()
        }])

        # Rows 2 & 3 -> Brew Type, Rest -> and Archetypes
        brew_stats = get_stats(df_battle_box, 'Brew', 'Brew Type')
        arch_stats = get_stats(df_battle_box, 'Archetype', 'Archetype')

        # Combine into the full stats table
        display_df = pd.concat([overall_row, brew_stats, arch_stats], ignore_index=True)

        # 3. Metallic Gray Styling
        def style_headers(row):
            if row['Cat'] == 'OVERALL':
                return ['background-color: rgba(44, 62, 80, 1); color: white;'] * len(row)
            elif (row['Cat'] == 'Meta' or row['Cat'] == 'Brew'):
                  return ['background-color: rgba(44, 62, 80, 0.63); color: white;'] * len(row)
            return [''] * len(row)

        styled_df = display_df.style.apply(style_headers, axis=1)
        
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Cat": "Category",
                "nº": st.column_config.NumberColumn("Decks", format="%d", width=60),
                "nº complete": st.column_config.NumberColumn("Done", format="%d", width=60),
                "% cards": st.column_config.ProgressColumn(
                    "Completion", 
                    format="%.1f%%", 
                    min_value=0, 
                    max_value=100,
                    color="rgb(255, 75, 75)"
                )
            }
        )

    # Top 12 Sets Widget
    with row_1_col_right:
        
        total_unique_sets = df_all_decks['edition'].nunique()

        st.markdown(f"## Sets in Battle Box: {total_unique_sets}")
        
        
        with st.container(border=True):

            st.markdown(f'''
                    <h3 style="margin: 0; padding-bottom: 0">Top 12 Sets</h3>
            ''', unsafe_allow_html=True)

            
            
            val_qty_select_col, count_select_col = st.columns(2)
            with val_qty_select_col:
                sort_m = st.radio("Rank Sets:", options=["Qty", "Val"], horizontal=True, key="set_rank_unique")
            with count_select_col:
                view_m = st.radio("Count Mode:", options=["All", "Unique"], horizontal=True, key="set_view_unique")

            # The clean one-line call
            fig_sets = features.get_top_sets_donut(df_all_decks, sort_m, view_m)
            
            if fig_sets:
                st.plotly_chart(fig_sets, use_container_width=True, key="sets_plot_unique")
            else:
                st.info("No set data available for this selection.")


def render_row_2(df_all_decks, df_battle_box):
    
    row_2_col_left, row_2_col_right = st.columns([1, 1], gap="small")
    
    with row_2_col_left:

        df_filtered_bb = df_battle_box.copy()

        with st.container(border=True):

            st.markdown("### Decks by Colors")
            
            # Archetype Filter
            archetypes = ["All", "Aggro", "Midrange", "Tempo", "Control", "Combo"]
            selected_arch = st.radio(
                "Filter by Archetype", 
                options=archetypes, 
                horizontal=True, 
                key="stats_arch_filter"
            )

            if selected_arch != "All":

                if 'Archetype' in df_filtered_bb.columns:
                    df_filtered_bb = df_filtered_bb[df_filtered_bb['Archetype'] == selected_arch]
                else:
                    st.warning("Archetype column not found in data.")

            if not df_filtered_bb.empty:

                # Named aggregation
                df_deck_identities = df_filtered_bb.groupby('Identity').agg(
                    n_decks=('DeckName', 'count'),
                    n_decks_complete=('CompletionPct', lambda x: (x == 100).sum()),
                    avg_main_complete=('CompletionPct', 'mean'),
                    avg_side_complete=('SideboardPct', 'mean')
                ).reset_index()

                df_deck_identities.columns = ['Identity', 'nº', 'nº complete', 'Main %', 'Side %']

                st.dataframe(
                    df_deck_identities.sort_values('nº', ascending=False),
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Identity": st.column_config.TextColumn("Color Identity", width="medium"),
                        "nº": st.column_config.NumberColumn("Decks", format="%d", width=70),
                        "nº complete": st.column_config.NumberColumn("Complete", format="%d", width=70), # Added this
                        "Main %": st.column_config.ProgressColumn(
                            "Mainboard", 
                            format="%.1f%%", 
                            min_value=0, 
                            max_value=100,
                            color="#34495e" # Dark Metallic Gray
                        ),
                        "Side %": st.column_config.ProgressColumn(
                            "Sideboard", 
                            format="%.1f%%", 
                            min_value=0, 
                            max_value=100,
                            color="#7f8c8d" 
                        )
                    }
                )
            else:
                st.info(f"No data available for archetype: {selected_arch}")

    with row_2_col_right:

        with st.container(border=True):

            st.markdown(f'''
                <div style="display: flex; justify-content: flex-start; align-items: flex-end; flex-wrap: wrap; margin-bottom: 10px;">
                    <h3 style="margin: 0; padding-bottom: 0">Cards by Colors</h3>
                    <p style="padding-bottom: 0; margin-bottom: 0; margin-left: 10px;">
                        <em style="font-size: 0.85rem; color: #888;">*Lands Excluded</em>
                    </p>
                </div>
            ''', unsafe_allow_html=True)
            
            is_trans = st.toggle("Transpose", key="inv_trans")

            rarity_select_col, counte_select_col = st.columns(2)

            with rarity_select_col:
                rarity_select = st.multiselect("Filter Rarity:", ['Common', 'Uncommon', 'Rare', 'Mythic'], key="inv_rarity")
            with counte_select_col:
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


def render_row_3(df_all_decks, df_battle_box):

    row_2_col_left, row_2_col_right = st.columns([1, 1], gap="small")

    with row_2_col_left:

        # Top 12 Staples Widget
        with st.container(border=True):

            st.markdown("### Top 12 Staples")
            
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

        pass

    # By Card Type Widget
    with row_2_col_right:

        with st.container(border=True):

            st.markdown("### Cards by Type")
            # --- INVENTORY VIEW CALL ---
            color_select_col, count_select_col = st.columns(2)

            with color_select_col:
                # Inventory usually shows all possible colors
                color_options = ['White', 'Blue', 'Black', 'Red', 'Green', 'Colorless', 'Multicolor']
                color_select = st.multiselect("Filter Color:", color_options, key="inv_type_col")

            with count_select_col:
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
    # CMC widget
    with st.container(border=True):
        # Header & Filter Row
        row_3_col_title, row_3_col_2, row_3_col_3, row_3_col_4 = st.columns([1, 1.5, 1.5, 0.8])
        
        with row_3_col_title: 
            st.markdown("### Mana Curve")
        with row_3_col_2:
            type_select = st.multiselect("Filter by Type:", options=['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment'], key="ds_cmc_type", label_visibility="collapsed")
        with row_3_col_3:
            color_select = st.multiselect("Filter by Color:", options=['White', 'Blue', 'Black', 'Red', 'Green', 'Colorless'], key="ds_cmc_color", label_visibility="collapsed")
        with row_3_col_4:
            is_trans = st.toggle("Transpose", key="ds_cmc_trans")

        # The clean refactored call
        # Adding sel_type and sel_color to the call to match the logic below
        fig_cmc = features.get_mana_curve_widget(
            df_all_decks, 
            'Inventory', 
            is_trans, 
            sel_type=type_select, 
            sel_color=color_select
        )

        if fig_cmc:
            st.plotly_chart(fig_cmc, use_container_width=True, config={'displayModeBar': False}, key="ds_cmc_chart")
        else:
            st.info("No cards match these filters...")


def render_bb_stats_view(df_all_decks, df_battle_box):
    # Pass df_all_decks and df_all_decks to your existing render_row_1 logic
    render_row_1(df_all_decks, df_battle_box) 
    render_row_2(df_all_decks, df_battle_box)
    st.divider()
    render_row_3(df_all_decks, df_battle_box)
    render_row_4(df_all_decks)