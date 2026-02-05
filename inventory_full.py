import streamlit as st
import pandas as pd
import features
import plotly.express as px

METALLIC_GRAY = "#2c3e50"

def render_row_1(df_inventory, df_all_decks):
    # --- Shared Column Configuration ---
    COL_WIDTHS = {"Stat": 120, "Short": 70, "Med": 90, "Long": 110}

    config_depth = {
        "Stat": st.column_config.TextColumn("Rarity", width=COL_WIDTHS["Stat"]),
        "Unique": st.column_config.NumberColumn("Unq", format="%d", width=COL_WIDTHS["Short"]),
        "Unq_Val": st.column_config.NumberColumn("Unq Val", format="$%.2f", width=COL_WIDTHS["Med"]),
        "Depth": st.column_config.NumberColumn("Depth", format="%.1fx", width=COL_WIDTHS["Short"]),
        "Count": st.column_config.NumberColumn("Total Qty", format="%d", width=COL_WIDTHS["Short"]),
        "Value": st.column_config.NumberColumn("Total Val", format="$%.2f", width=COL_WIDTHS["Med"]),
    }

    config_decks = {
        "Stat": st.column_config.TextColumn("Rarity", width=COL_WIDTHS["Stat"]),
        "In_Decks_Unq": st.column_config.NumberColumn("Unq in Deck", format="%d", width=COL_WIDTHS["Long"]),
        "Usage_Unq_Pct": st.column_config.ProgressColumn("% Unq Used", format="%.1f%%", min_value=0, max_value=100, width=COL_WIDTHS["Long"]),
        "In_Decks_Qty": st.column_config.NumberColumn("Total in Deck", format="%d", width=COL_WIDTHS["Long"]),
        "Usage_Pct": st.column_config.ProgressColumn("% Total Used", format="%.1f%%", min_value=0, max_value=100, width=COL_WIDTHS["Long"]),
        "In_Decks_Val": st.column_config.NumberColumn("Val in Decks", format="$%.2f", width=COL_WIDTHS["Long"])
    }

    row_1_col_left, row_1_col_right = st.columns([1, 1], gap="small")

    # Comparative Tables Widget
    with row_1_col_left:
        # 1. CLEAN AND NORMALIZE BOTH DATAFRAMES
        # Force everything to string, strip, title case, and handle potential NaNs
        inv_clean = df_inventory.copy()
        inv_clean['rarity'] = inv_clean['rarity'].fillna("Unknown").astype(str).str.strip().str.title()
        
        decks_clean = df_all_decks.copy()
        decks_clean['rarity'] = decks_clean['rarity'].fillna("Unknown").astype(str).str.strip().str.title()

        # Mapping for consistency
        rarity_map = {
            'Mythicrare': 'Mythic', 
            'Mythic Rare': 'Mythic',
            'Basicland': 'Basic Land' # Fixing the spacing while we are at it
        }

        for df in [inv_clean, decks_clean]:
            df['rarity'] = df['rarity'].astype(str).str.strip().str.title()
            df['rarity'] = df['rarity'].replace(rarity_map)
            
        # 2. PREP INVENTORY DATA
        inv_total = inv_clean.groupby('rarity').agg(
            Count=('qty', 'sum'),
            Value=('total_cards_value', 'sum')
        ).reset_index()

        inv_unq_base = inv_clean.assign(unq_qty=1)
        inv_unq_base['unit_price'] = inv_unq_base['total_cards_value'] / inv_unq_base['qty'].replace(0, 1)
        
        inv_unq_agg = inv_unq_base.groupby('rarity').agg(
            Unique=('unq_qty', 'sum'),
            Unq_Val=('unit_price', 'sum')
        ).reset_index()

        # Create df_depth and ensure 'Stat' is solid
        df_depth = pd.merge(inv_total, inv_unq_agg, on='rarity').rename(columns={'rarity': 'Stat'})
        df_depth['Depth'] = (df_depth['Count'] / df_depth['Unique']).fillna(0)

        # 3. PREP DECK DATA
        deck_stats = decks_clean.assign(unq_in_deck=1).groupby('rarity').agg(
            In_Decks_Unq=('unq_in_deck', 'sum'),
            In_Decks_Qty=('qty', 'sum'),
            In_Decks_Val=('total_cards_value', 'sum')
        ).reset_index().rename(columns={'rarity': 'Stat'})

        # 4. THE CRITICAL MERGE
        # We use 'outer' here as a safety measure: if a rarity exists in decks but 
        # somehow not in inventory, it will STILL show up in the table instead of vanishing.
        df_usage = pd.merge(deck_stats, df_depth[['Stat', 'Unique', 'Count']], on='Stat', how='outer')
        
        # Fill missing merge keys (if any) so the row has a label
        df_usage['Stat'] = df_usage['Stat'].fillna("Unknown")
        
        # Fill denominator NaNs with 0 then replace with 1 for division
        df_usage['Unique'] = df_usage['Unique'].fillna(0)
        df_usage['Count'] = df_usage['Count'].fillna(0)

        # Calculate percentages
        df_usage['Usage_Unq_Pct'] = (df_usage['In_Decks_Unq'] / df_usage['Unique'].replace(0, 1) * 100).fillna(0)
        df_usage['Usage_Pct'] = (df_usage['In_Decks_Qty'] / df_usage['Count'].replace(0, 1) * 100).fillna(0)
        
        # Drop math helpers
        df_usage_clean = df_usage.drop(columns=['Unique', 'Count']).fillna(0)

        # --- SUMMARY ROWS ---
        summary_depth = pd.DataFrame([{
            'Stat': 'Total Cards',
            'Unique': df_depth['Unique'].sum(),
            'Unq_Val': df_depth['Unq_Val'].sum(),
            'Depth': (df_depth['Count'].sum() / df_depth['Unique'].sum()) if df_depth['Unique'].sum() > 0 else 0,
            'Count': df_depth['Count'].sum(),
            'Value': df_depth['Value'].sum()
        }])

        summary_usage = pd.DataFrame([{
            'Stat': 'Total Cards',
            'In_Decks_Unq': deck_stats['In_Decks_Unq'].sum(),
            'Usage_Unq_Pct': (deck_stats['In_Decks_Unq'].sum() / df_depth['Unique'].sum() * 100) if df_depth['Unique'].sum() > 0 else 0,
            'In_Decks_Qty': deck_stats['In_Decks_Qty'].sum(),
            'Usage_Pct': (deck_stats['In_Decks_Qty'].sum() / df_depth['Count'].sum() * 100) if df_depth['Count'].sum() > 0 else 0,
            'In_Decks_Val': deck_stats['In_Decks_Val'].sum()
        }])

        # --- RENDER TABLES ---
        st.subheader("Collection Depth")
        st.dataframe(
            pd.concat([summary_depth, df_depth.sort_values('Count', ascending=False)], ignore_index=True).style.apply(
                lambda s: [f'background-color: {METALLIC_GRAY}; color: white;' if s.name == 0 else '' for _ in s], axis=1
            ),
            use_container_width=True, hide_index=True, column_config=config_depth
        )

        st.subheader("Deck Integration")
        # Using 'summary_usage' which pulls directly from deck_stats to ensure the Total is always accurate
        st.dataframe(
            pd.concat([summary_usage, df_usage_clean[df_usage_clean['Stat'] != 'Total Cards'].sort_values('In_Decks_Qty', ascending=False)], ignore_index=True).style.apply(
                lambda s: [f'background-color: {METALLIC_GRAY}; color: white;' if s.name == 0 else '' for _ in s], axis=1
            ),
            use_container_width=True, hide_index=True, column_config=config_decks
        )

    # Top 12 Sets Widget
    with row_1_col_right:
        with st.container(border=True):
            st.markdown("### Top 12 Sets")
    
            f_col1, f_col2 = st.columns(2)
            with f_col1:
                sort_m = st.radio("Rank Sets:", options=["Qty", "Val"], horizontal=True, key="set_rank_unique")
            with f_col2:
                view_m = st.radio("Count Mode:", options=["All", "Unique"], horizontal=True, key="set_view_unique")

            # The clean one-line call
            fig_sets = features.get_top_sets_donut(df_inventory, sort_m, view_m)
            
            if fig_sets:
                st.plotly_chart(fig_sets, use_container_width=True, key="sets_plot_unique")
            else:
                st.info("No set data available for this selection.")


def render_row_2(df_inventory):

    row_2_col_left, row_2_col_right = st.columns([1, 1], gap="small")

    # By Color Widget
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
                df_inventory,
                is_trans,
                rarity_select,
                count_select=count_select
            )
            if fig_colors:
                st.plotly_chart(fig_colors, use_container_width=True, key="inv_color_plot")
            else:
                st.info("No cards found for this selection.")

    # By Card Type Widget
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
                df_inventory, 
                color_select, 
                count_select=count_select
            )

            if fig_types:
                st.plotly_chart(fig_types, use_container_width=True, key="inv_type_plot")
            else:
                st.info("No cards found in your inventory for this selection.")


def render_row_3(df_inventory):

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
        fig_cmc = features.get_mana_curve_widget(df_inventory, type_select, color_select, is_trans)

        if fig_cmc:
            st.plotly_chart(fig_cmc, use_container_width=True, config={'displayModeBar': False}, key="ds_cmc_chart")
        else:
            st.info("No cards match these filters...")


def render_inventory_stats_view(df_inventory, df_all_decks):
    # Pass df_inventory and df_all_decks to your existing render_row_1 logic
    render_row_1(df_inventory, df_all_decks) 
    render_row_2(df_inventory)
    st.divider()
    render_row_3(df_inventory)