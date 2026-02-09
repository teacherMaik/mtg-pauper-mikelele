import streamlit as st
import pandas as pd
import features

METALLIC_GRAY = "#2c3e50"

def get_land_categorized_df(df):
    """Assigns a 'land_group' label to each row based on your hierarchy."""
    if df.empty:
        return df
    
    df_l = df[df['type'].str.contains('Land', na=False, case=False)].copy()
    
    # Define hierarchy logic
    def assign_group(row):
        if row['is_basic'] and not row['is_snow']: return "Basics"
        if row['is_basic'] and row['is_snow']: return "Snow Basics"
        if row['is_artifact'] and row['is_dual']: return "Artifact Duals"
        if row['is_artifact']: return "Artifact"
        if row['is_dual'] and row['is_snow']: return "Snow Duals"
        if row['is_dual']: return "Duals"
        return "Others"

    df_l['land_group'] = df_l.apply(assign_group, axis=1)
    return df_l


def render_row_1(df_inventory, df_all_decks):
    # --- Shared Column Configuration ---
    COL_WIDTHS = {"Stat": 130, "Short": 75, "Med": 95, "Long": 115}

    config_depth = {
        "Stat": st.column_config.TextColumn("Land Type", width=COL_WIDTHS["Stat"]),
        "Unique": st.column_config.NumberColumn("Unq", format="%d", width=COL_WIDTHS["Short"]),
        "Unq_Val": st.column_config.NumberColumn("Unq Val", format="$%.2f", width=COL_WIDTHS["Med"]),
        "Depth": st.column_config.NumberColumn("Depth", format="%.1fx", width=COL_WIDTHS["Short"]),
        "Count": st.column_config.NumberColumn("Total Qty", format="%d", width=COL_WIDTHS["Short"]),
        "Value": st.column_config.NumberColumn("Total Val", format="$%.2f", width=COL_WIDTHS["Med"]),
    }

    config_decks = {
        "Stat": st.column_config.TextColumn("Land Type", width=COL_WIDTHS["Stat"]),
        "In_Decks_Unq": st.column_config.NumberColumn("Unq in Deck", format="%d", width=COL_WIDTHS["Long"]),
        "Usage_Unq_Pct": st.column_config.ProgressColumn("% Unq Used", format="%.1f%%", min_value=0, max_value=100, width=COL_WIDTHS["Long"]),
        "In_Decks_Qty": st.column_config.NumberColumn("Total in Deck", format="%d", width=COL_WIDTHS["Long"]),
        "Usage_Pct": st.column_config.ProgressColumn("% Total Used", format="%.1f%%", min_value=0, max_value=100, width=COL_WIDTHS["Long"]),
        "In_Decks_Val": st.column_config.NumberColumn("Val in Decks", format="$%.2f", width=COL_WIDTHS["Long"])
    }

    row_1_col_left, row_1_col_right = st.columns([1.1, 0.9], gap="small")

    with row_1_col_left:
        # 1. CATEGORIZE
        inv_lands = get_land_categorized_df(df_inventory)
        deck_lands = get_land_categorized_df(df_all_decks)

        # 2. PREP INVENTORY DEPTH
        inv_total = inv_lands.groupby('land_group').agg(Count=('qty', 'sum'), Value=('total_cards_value', 'sum')).reset_index()
        
        inv_unq_base = inv_lands.assign(unq_qty=1)
        inv_unq_base['unit_price'] = inv_unq_base['total_cards_value'] / inv_unq_base['qty'].replace(0, 1)
        inv_unq_agg = inv_unq_base.groupby('land_group').agg(Unique=('unq_qty', 'sum'), Unq_Val=('unit_price', 'sum')).reset_index()

        df_depth = pd.merge(inv_total, inv_unq_agg, on='land_group').rename(columns={'land_group': 'Stat'})
        df_depth['Depth'] = (df_depth['Count'] / df_depth['Unique']).fillna(0)

        # 3. PREP DECK USAGE
        deck_stats = deck_lands.assign(unq_in_deck=1).groupby('land_group').agg(
            In_Decks_Unq=('unq_in_deck', 'sum'),
            In_Decks_Qty=('qty', 'sum'),
            In_Decks_Val=('total_cards_value', 'sum')
        ).reset_index().rename(columns={'land_group': 'Stat'})

        # 4. MERGE & CALC PCT
        df_usage = pd.merge(deck_stats, df_depth[['Stat', 'Unique', 'Count']], on='Stat', how='outer').fillna(0)
        df_usage['Usage_Unq_Pct'] = (df_usage['In_Decks_Unq'] / df_usage['Unique'].replace(0, 1) * 100).fillna(0)
        df_usage['Usage_Pct'] = (df_usage['In_Decks_Qty'] / df_usage['Count'].replace(0, 1) * 100).fillna(0)
        df_usage_clean = df_usage.drop(columns=['Unique', 'Count'])

        # --- SUMMARY ROWS ---
        summary_depth = pd.DataFrame([{
            'Stat': 'TOTAL LANDS',
            'Unique': df_depth['Unique'].sum(), 'Unq_Val': df_depth['Unq_Val'].sum(),
            'Depth': (df_depth['Count'].sum() / df_depth['Unique'].sum()) if df_depth['Unique'].sum() > 0 else 0,
            'Count': df_depth['Count'].sum(), 'Value': df_depth['Value'].sum()
        }])

        summary_usage = pd.DataFrame([{
            'Stat': 'TOTAL LANDS',
            'In_Decks_Unq': deck_stats['In_Decks_Unq'].sum(),
            'Usage_Unq_Pct': (deck_stats['In_Decks_Unq'].sum() / df_depth['Unique'].sum() * 100) if df_depth['Unique'].sum() > 0 else 0,
            'In_Decks_Qty': deck_stats['In_Decks_Qty'].sum(),
            'Usage_Pct': (deck_stats['In_Decks_Qty'].sum() / df_depth['Count'].sum() * 100) if df_depth['Count'].sum() > 0 else 0,
            'In_Decks_Val': deck_stats['In_Decks_Val'].sum()
        }])

        # --- RENDER ---
        st.markdown("### Land Depth")
        st.dataframe(
            pd.concat([summary_depth, df_depth.sort_values('Count', ascending=False)], ignore_index=True).style.apply(
                lambda s: [f'background-color: {METALLIC_GRAY}; color: white;' if s.name == 0 else '' for _ in s], axis=1
            ), use_container_width=True, hide_index=True, column_config=config_depth
        )

        st.markdown("### Deck Integration")
        st.dataframe(
            pd.concat([summary_usage, df_usage_clean[df_usage_clean['Stat'] != 'TOTAL LANDS'].sort_values('In_Decks_Qty', ascending=False)], ignore_index=True).style.apply(
                lambda s: [f'background-color: {METALLIC_GRAY}; color: white;' if s.name == 0 else '' for _ in s], axis=1
            ), use_container_width=True, hide_index=True, column_config=config_decks
        )

    # --- RIGHT COLUMN: TOP LAND SETS ---
    with row_1_col_right:
        land_only_inv = df_inventory[df_inventory['type'].str.contains('Land', na=False)].copy()
        total_unq_sets = land_only_inv['edition'].nunique()

        st.markdown(f"### Land Sets: {total_unq_sets}")
        with st.container(border=True):
            st.markdown('<h4 style="margin:0">Top 12 Land Sets</h4>', unsafe_allow_html=True)
            f1, f2 = st.columns(2)
            with f1: s_m = st.radio("Rank:", ["Qty", "Val"], horizontal=True, key="l_rank")
            with f2: v_m = st.radio("Mode:", ["All", "Unique"], horizontal=True, key="l_view")

            df_donut = land_only_inv.copy()
            if v_m == "Unique":
                df_donut['qty'] = 1
                df_donut['total_cards_value'] = df_donut['price']

            set_agg = features.get_top_sets_aggregate(df_donut)
            fig = features.get_top_sets_donut(set_agg, s_m)
            if fig: st.plotly_chart(fig, use_container_width=True, key="land_set_donut_chart")


def render_row_2(df_inventory, df_all_decks, df_battle_box):

    row_2_col_left, row_2_col_right = st.columns([1, 1], gap="medium")

    # --- LEFT: MANA SATURATION (Toggleable) ---
    with row_2_col_left:
        st.markdown("### Lands By Color")
        source_mode = st.radio(
            "Source:", ["Inventory", "Decks"], 
            horizontal=True, key="l_sat_src", label_visibility="collapsed"
        )
        
        # Decide source for Saturation
        sat_raw_df = df_inventory if source_mode == "Inventory" else df_all_decks
        
        # 1. LAND-SPECIFIC AGGREGATION (Filters for Lands inside features.py)
        land_df_clean, total_qty = features.get_land_mana_saturation_agg(sat_raw_df)

        if total_qty > 0:
            fig_sat = features.get_color_saturation_widget(land_df_clean, total_qty, is_transposed=True)
            st.plotly_chart(fig_sat, use_container_width=True, key=f"sat_{source_mode}")
        else:
            st.info(f"No land production data in {source_mode}.")

    # --- RIGHT: TOP 12 STAPLES (Locked to Decks) ---
    with row_2_col_right:
        with st.container(border=True):
            st.markdown("### Top 12 Land Staples")
            st.caption('*Basic Lands Excluded')
            
            # Simplified filter: Archetype only
            archetype_filter = st.radio(
                "Archetype:", ["All", "Aggro", "Midrange", "Tempo", "Control", "Combo"], 
                horizontal=True, key="land_staple_arch"
            )

            # 1. Prepare Base Data
            deck_col = 'DeckName'
            df_staple_base = df_all_decks.merge(
                df_battle_box[[deck_col, 'Archetype']], on=deck_col, how='left'
            )

            # 2. FILTER FOR NON-BASIC LANDS
            # We want cards that ARE lands but ARE NOT basic
            land_staple_mask = (
                (df_staple_base['type'].str.contains('Land', case=False, na=False)) & 
                (df_staple_base['is_basic'] == False)
            )
            
            df_to_use = df_staple_base[land_staple_mask]

            # 3. Apply Archetype Filter
            if archetype_filter != "All":
                df_to_use = df_to_use[df_to_use['Archetype'] == archetype_filter]

            # 4. Aggregate and Render
            # Using your existing staples logic from features.py
            top_12_data = features.get_top_12_staples_aggregate(df_to_use)
            
            if not top_12_data.empty:
                fig_heat = features.get_top_12_staples_widget(top_12_data, deck_col)
                st.plotly_chart(fig_heat, use_container_width=True, config={'displayModeBar': False})
            else:
                st.info(f"No non-basic lands found for {archetype_filter}")


def render_row_3(df_inventory, df_all_decks):
    
    # 1. PREP DATA
    df_explorer = df_inventory[df_inventory['type'].str.contains('Land', na=False)].copy()
    
    # 2. SEARCH LOGIC
    search_query = st.text_input(
        "Search by Name or Tag (e.g., 'surveil', 'fetch', 'cycler', 'gate')...", 
        placeholder="Type a card name or a property...",
        key="land_explorer_search"
    ).strip().lower()

    if search_query:
        potential_col = f"is_{search_query}"
        if potential_col in df_explorer.columns:
            df_explorer = df_explorer[df_explorer[potential_col] == True]
        else:
            df_explorer = df_explorer[df_explorer['name'].str.contains(search_query, case=False, na=False)]

    # 3. LAYOUT COLS [2, 1]
    col_left, col_right = st.columns([2, 1], gap="medium")

    with col_left:
        st.markdown("### 🔍 Global Land Explorer")
        
        df_display = df_explorer[[
            'name', 'edition', 'land_mana', 'type', 'qty', 'price'
        ]].sort_values('name')

        event = st.dataframe(
            df_display,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            column_config={
                "qty": st.column_config.NumberColumn("Qty", width=40),
                "name": st.column_config.TextColumn("Card Name", width="medium"),
                "edition": st.column_config.TextColumn("Set", width="Large"),
                "land_mana": st.column_config.TextColumn("Produces", width="Small"),
                "type": st.column_config.TextColumn("Type Line", width="medium"),
                "price": st.column_config.NumberColumn("Price", format="$%.2f"),
            }
        )
        st.caption(f"Showing {len(df_explorer)} lands. Click a row to view deck requirements.")

        # --- DECK USAGE TABLE ---
        if event and len(event.selection.rows) > 0:
            selected_idx = event.selection.rows[0]
            selected_card_name = df_display.iloc[selected_idx]['name']

            usage_df = df_all_decks[df_all_decks['name'] == selected_card_name].copy()
            total_owned = df_inventory[df_inventory['name'] == selected_card_name]['qty'].sum()

            st.markdown(f"#### Usage for **{selected_card_name}**")

            if not usage_df.empty:
                # Group by DeckName to get both Required and the specific Allocated count
                deck_summary = usage_df.groupby('DeckName').agg(
                    Required=('qty', 'sum'),
                    Allocated=('num_for_deck', 'sum')
                ).reset_index()
                
                st.dataframe(
                    deck_summary,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "DeckName": "Deck",
                        "Required": st.column_config.NumberColumn("Needed", width=70, help="Quantity required by the decklist"),
                        "Allocated": st.column_config.NumberColumn("Assigned", width=70, help="Actual copies currently allocated to this deck")
                    }
                )
            else:
                st.info(f"**{selected_card_name}** is not found in any active decks.")

    # 4. CARD DISPLAY
    with col_right:
        if event and len(event.selection.rows) > 0:
            # We already have selected_card_name from the logic above
            card_info = df_inventory[df_inventory['name'] == selected_card_name].iloc[0]
            st.image(card_info['image_url'], use_container_width=True)
        else:
            st.info("Select a land to view image and deck availability.")


def render_land_fan_view(df_inventory, df_all_decks, df_battle_box):
    
    render_row_1(df_inventory, df_all_decks)
    st.divider()
    render_row_2(df_inventory, df_all_decks, df_battle_box)
    st.divider()
    render_row_3(df_inventory, df_all_decks)
    
    
    