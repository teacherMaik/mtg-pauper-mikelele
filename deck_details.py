import streamlit as st
import pandas as pd
import features

def render_deck_detail(deck_name, df_inventory, df_all_decks, df_battle_box):

    deck_cards = df_all_decks[df_all_decks['DeckName'] == deck_name].copy()
    
    # --- ROW 1: HEADER & NAVIGATION ---
    deck_value = deck_cards['total_cards_value'].sum()
    st.markdown(f"""
        <div style="line-height: 1.1;">
            <h2 style="margin: 0; padding: 3px; font-size: 2.2rem;">{deck_name}</h2>
            <div style="font-size: 26px; font-weight: 700; color: #34495e; margin-top: padding: 3px;">
                ~ ${deck_value:,.2f}
            </div>
        </div>
    """, unsafe_allow_html=True)

    deck_view_mode = st.radio(
        "Select View:",
        ["Deck", "Analysis", "Test"],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.divider()

    # --- VIEW ROUTING ---
    if deck_view_mode == "Deck":
        render_deck_list_view(deck_cards)
    elif deck_view_mode == "Analysis":
        render_deck_stats_view(deck_cards)
    elif deck_view_mode == "Test":
        st.info("Test View - Coming next")


def render_deck_list_view(deck_cards):

    # 2. Status Logic (using your exact col names)
    deck_cards['status'] = deck_cards.apply(
        lambda x: "✅" if x['num_for_deck'] >= x['qty'] else f"({int(x['num_for_deck'])}/{int(x['qty'])})", 
        axis=1
    )

    # Separate Main vs Side
    mainboard = deck_cards[deck_cards['section'].str.contains('Main', case=False, na=False)]
    sideboard = deck_cards[deck_cards['section'].str.contains('Side', case=False, na=False)]
    
    cards_main = mainboard['qty'].sum()
    cards_main_collected = mainboard['num_for_deck'].sum()
    main_pct = (cards_main_collected / cards_main * 100) if cards_main > 0 else 0
    value_main = mainboard['total_cards_value'].sum()

    cards_side = sideboard['qty'].sum()
    cards_side_collected = sideboard['num_for_deck'].sum()
    side_pct = (cards_side_collected / cards_side * 100) if cards_side > 0 else 0
    value_side = sideboard['total_cards_value'].sum()

    if deck_cards.empty:
        st.error("Deck data not found.")
        return
    
    st.markdown(f"""
        <div style="margin-top:-15px; margin-bottom:15px;">
            <div style="font-size:26px; font-weight:500; margin-bottom:5px;">
                Main ({int(cards_main)}) ~ ${value_main:,.2f}
            </div>
            <div style="background-color: #e0e0e0; border-radius: 5px; width: 210px; height: 8px;">
                <div style="background-color: #34495e; width: {main_pct}%; height: 8px; border-radius: 5px;"></div>
            </div>
            <div style="font-size: 12px; color: #666; margin-top: 2px;">
                {int(cards_main_collected)} / {int(cards_main)} cards collected ({main_pct:.1f}%)
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 4. Mainboard Layout (Wrapped by Type)
    col_left, col_right = st.columns(2, gap="large")
    
    left_types = ['Creature', 'Instant', 'Sorcery']
    right_types = ['Enchantment', 'Artifact', 'Land']

    def draw_type_groups(df, types, ui_col):
        
        with ui_col:
            for t in types:
                # SPECIAL LOGIC: If checking Artifacts, exclude Lands
                if t == 'Artifact':
                    subset = df[
                        (df['type'].str.contains('Artifact', case=False, na=False)) & 
                        (~df['type'].str.contains('Land', case=False, na=False))
                    ]
                else:
                    subset = df[df['type'].str.contains(t, case=False, na=False)]
                
                if not subset.empty:
                    
                    st.markdown(f"#### {t}s ({int(subset['qty'].sum())})")
                    st.dataframe(
                        subset[['qty', 'name', 'mana', 'total_cards_value', 'status']].sort_values("name"),
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "status": st.column_config.TextColumn("Collected", width=65),
                            "qty": st.column_config.NumberColumn("Qty", format="%d", width=35),
                            "name": st.column_config.TextColumn("Name"),
                            "mana": st.column_config.TextColumn("Mana", width=80),
                            "total_cards_value": st.column_config.NumberColumn("Value", format="$ %.2f", width=60)
                        }
                    )
                else:
                    st.markdown(f"""
                        <div style="padding: 15px; border-left: 5px solid #ff4b4b;; background-color: #f8f9fa; color: #34495e; border-radius: 4px; margin-bottom: 20px;">
                            No {t}s in this deck.
                        </div>
                    """, unsafe_allow_html=True)

    draw_type_groups(mainboard, left_types, col_left)
    draw_type_groups(mainboard, right_types, col_right)

    st.divider()

    # 5. Sideboard (Full width below)
    if not sideboard.empty:

        side_col_left, side_col_right = st.columns(2, gap="large")
        

        with side_col_left:
            st.markdown(f"""
                <div style="margin-top:-15px; margin-bottom:15px;">
                    <div style="font-size:26px; font-weight:500; margin-bottom:5px;">
                        Side ({int(cards_side)}) ~ ${value_side:,.2f}
                    </div>
                    <div style="background-color: #e0e0e0; border-radius: 5px; width: 210px; height: 8px;">
                        <div style="background-color: #34495e; width: {side_pct}%; height: 8px; border-radius: 5px;"></div>
                    </div>
                    <div style="font-size: 12px; color: #666; margin-top: 2px;">
                        {int(cards_side_collected)} / {int(cards_side)} cards collected ({side_pct:.1f}%)
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.dataframe(
                sideboard[['qty', 'name', 'type', 'mana', 'total_cards_value', 'status', ]].sort_values("name"),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "status": st.column_config.TextColumn("Collected", width=45),
                    "qty": st.column_config.NumberColumn("Qty", format="%d", width=35),
                    "name": st.column_config.TextColumn("Name"),
                    "type": st.column_config.TextColumn("Type"),
                    "mana": st.column_config.TextColumn("Mana", width=60),
                    "total_cards_value": st.column_config.NumberColumn("Value", format="$ %.2f", width=60)
                }
            )

        with side_col_right:
            pass


def render_deck_stats_view(deck_cards):
    
    
    # Color and Card Type Stats Row
    row_2_col_left, row_2_col_right = st.columns(2)

    # --- LEFT COLUMN: COLOR SATURATION ---
    with row_2_col_left:
        with st.container(border=True):

            # Header
            st.markdown('''
                <div style="display: flex; justify-content: flex-start; align-items: flex-end; flex-wrap: wrap; margin-bottom: 10px;">
                    <h3 style="margin: 0; padding-bottom: 0">Cards by Colors</h3>
                    <p style="padding-bottom: 0; margin-bottom: 0; margin-left: 10px;">
                        <em style="font-size: 0.85rem; color: #888;">*Lands Excluded</em>
                    </p>
                </div>
            ''', unsafe_allow_html=True)
            
            # Dynamic Rarity Discovery
            # Convert 'MythicRare' back to 'Mythic' for UI consistency
            raw_rarities = deck_cards['rarity'].replace({'MythicRare': 'Mythic'}).unique()
            # Ensure they stay in a logical order
            rarity_order = ['Common', 'Uncommon', 'Rare', 'Mythic']
            dynamic_rarities = [r for r in rarity_order if r in raw_rarities]

            # 2. Controls
            is_trans = st.toggle("Transpose", key="ds_trans")
            c1, c2 = st.columns(2)
            
            with c1:
                # Only displays rarities that exist in deck_cards
                sel_r = st.multiselect("Filter Rarity:", options=dynamic_rarities, key="ds_rarity")
            
            with c2:
                # This string ("Main", "Side", or "Both") is passed to the 'is_deck' parameter
                deck_section_mode = st.radio("Section:", ["Main", "Side", "Both"], horizontal=True, key="ds_view")

            # 3. The Refactored One-Line Call
            # Note: count_select defaults to "All", so we don't need to pass it for Decks
            fig_color = features.get_color_saturation_widget(
                deck_cards,
                is_trans,
                sel_r,
                is_deck=deck_section_mode
            )
            
            if fig_color:
                st.plotly_chart(fig_color, use_container_width=True, key="ds_color_plot")
            else:
                st.info("No cards match the selected type filters.")

    # --- RIGHT COLUMN: TYPE DISTRIBUTION ---
    with row_2_col_right:
        with st.container(border=True):

            st.markdown('<h3 style="margin: 0; margin-bottom: 10px;">Cards by Type</h3>', unsafe_allow_html=True)
            
            # --- DECK VIEW CALL ---
            t1, t2 = st.columns(2)

            with t1:
                # Logic to only show colors actually present in this specific deck
                present_codes = deck_cards['color'].unique()
                db_to_ui = {'W': 'White', 'U': 'Blue', 'B': 'Black', 'R': 'Red', 'G': 'Green', 'C': 'Colorless'}
                available_colors = [db_to_ui[code] for code in present_codes if code in db_to_ui]
                if (deck_cards['is_multi_colored'] == True).any():
                    available_colors.append('Multicolor')
                
                sel_c = st.multiselect("Filter Color:", available_colors, key="ds_type_col")

            with t2:
                # In Deck View, we filter by Section instead of Count Mode
                ds_section = st.radio("Section:", ["Main", "Side", "Both"], horizontal=True, key="ds_type_sec")

            # The call uses the 'is_deck' parameter. count_select defaults to 'All' internally.
            fig_type = features.get_type_distribution_widget(
                deck_cards, 
                sel_c, 
                is_deck=ds_section
            )

            if fig_type:
                st.plotly_chart(fig_type, use_container_width=True, key="ds_type_plot")
            else:
                st.info("No cards match the selected filters for this deck.")

    # ROW 3: TOP SETS (Full Width or Column based on your preference)
    with st.container(border=True):
        # Header & Filter Row
        c_head, c_f1, c_f2, c_f3 = st.columns([1, 1.5, 1.5, 0.8])
        with c_head: 
            st.markdown("### Mana Curve")
        with c_f1:
            s_type = st.multiselect("Filter by Type:", options=['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment'], key="ds_cmc_type", label_visibility="collapsed")
        with c_f2:
            s_color = st.multiselect("Filter by Color:", options=['White', 'Blue', 'Black', 'Red', 'Green', 'Colorless'], key="ds_cmc_color", label_visibility="collapsed")
        with c_f3:
            is_trans = st.toggle("Transpose", key="ds_cmc_trans")

        # The clean refactored call
        fig_cmc = features.get_mana_curve_widget(deck_cards, s_type, s_color, is_trans)

        if fig_cmc:
            st.plotly_chart(fig_cmc, use_container_width=True, config={'displayModeBar': False}, key="ds_cmc_chart")
        else:
            st.info("No cards match these filters...")

    return