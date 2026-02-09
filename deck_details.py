import streamlit as st
import pandas as pd
import features
import plotly.express as px
import random

def render_deck_detail(deck_name, df_inventory, df_all_decks, df_battle_box):

    deck_cards = df_all_decks[df_all_decks['DeckName'] == deck_name].copy()
    
    # --- ROW 1: HEADER & NAVIGATION ---
    deck_value = deck_cards['total_cards_value'].sum()
    st.markdown(f"""
        <div style="line-height: 1.1;">
            <h2 style="margin: 0; padding: 3px; font-size: 2.2rem;">{deck_name}</h2>
            <h3 style="font-size: 26px; font-weight: 700; color: #34495e; margin-top: 0; padding: 0 0 7px;">~ ${deck_value:,.2f}</h3>
        </div>
    """, unsafe_allow_html=True)


    """deck_view_mode = st.radio(
        "Select View:",
        ["Deck", "Analysis", "Test"],
        horizontal=True,
        label_visibility="collapsed"
    )"""

    # 3. INTERNAL NAVIGATION
    if "deck_sub_view" not in st.session_state:
        st.session_state.deck_sub_view = "Deck"

    sub_view_options = {
        "Deck": "Deck",
        "Analysis": "Analysis", 
        "test_deck": "Test"
    }

    # Use 'default' instead of 'value'
    selected_label = st.segmented_control(
        "Select View:",
        options=list(sub_view_options.keys()),
        format_func=lambda x: sub_view_options[x],
        selection_mode="single",
        default=st.session_state.deck_sub_view,
        label_visibility="collapsed",
        key="deck_internal_nav"
    )

    # Sync state and rerun if changed
    if selected_label and selected_label != st.session_state.deck_sub_view:
        st.session_state.deck_sub_view = selected_label
        st.rerun()


    st.divider()

    # --- VIEW ROUTING ---
    current_mode = st.session_state.deck_sub_view

    if current_mode == "Deck":
        st.session_state.active_view = "Deck"
        render_deck_list_view(deck_cards)
    elif current_mode == "Analysis":
        st.session_state.active_view = "Analysis"
        render_deck_stats_view(deck_cards)
    elif current_mode == "test_deck":
        # 1. Check if we are "new" to this mode
        if st.session_state.get("active_view") != "test_deck":
            # Clear the old data
            for key in ['shuffled_library', 'hand', 'ptr', 'draw_counter', 'hand_selector']:
                st.session_state.pop(key, None)
            
            # 2. Set the 'gate' so this block doesn't run again while we are playtesting
            st.session_state.active_view = "test_deck"

        # 3. Now call the function
        render_test_deck_view(deck_cards)


def render_deck_list_view(deck_cards):
    
    if deck_cards.empty:
        st.error("Deck data not found.")
        return

    current_deck_id = deck_cards['DeckName'].iloc[0]
    
    # Wipe state if we switch decks
    if "active_view_deck" not in st.session_state or st.session_state.active_view_deck != current_deck_id:
        st.session_state.selected_card = None
        st.session_state.active_view_deck = current_deck_id

    # --- 2. DATA PREP ---
    deck_cards['status'] = deck_cards.apply(
        lambda x: "✅" if x['num_for_deck'] >= x['qty'] else f"({int(x['num_for_deck'])}/{int(x['qty'])})", 
        axis=1
    )
    
    mainboard = deck_cards[deck_cards['section'].str.contains('Main', case=False, na=False)]
    sideboard = deck_cards[deck_cards['section'].str.contains('Side', case=False, na=False)]
    
    cards_main = mainboard['qty'].sum()
    value_main = mainboard['total_cards_value'].sum()
    main_pct = (mainboard['num_for_deck'].sum() / cards_main * 100) if cards_main > 0 else 0
    
    # --- 3. HEADER ---
    st.markdown(f"""
        <div style="margin-top:-15px; margin-bottom:15px;">
            <div style="font-size:26px; font-weight:500; margin-bottom:5px;">Main ({int(cards_main)}) ~ ${value_main:,.2f}</div>
            <div style="display: flex; align-items: center;">
                <div style="background-color: #e0e0e0; border-radius: 5px; width: 210px; height: 8px;">
                    <div style="background-color: #34495e; width: {main_pct}%; height: 8px; border-radius: 5px;"></div>
                </div>
                <p style="margin-left: 10px; margin-bottom: 0; font-size: 12px;">{main_pct:.1f}%</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # --- 4. CSS FOR CENTERING ---
    st.markdown("""
        <style>
        .centered-preview {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            text-align: center;
        }
        </style>
    """, unsafe_allow_html=True)

    # --- 5. MAINBOARD GRID ---
    col_left, col_right = st.columns(2, gap="large")
    left_types = ['Creature', 'Instant', 'Sorcery']
    right_types = ['Enchantment', 'Artifact', 'Land', 'Planeswalker']

    def draw_type_table(df, t, ui_col):
        with ui_col:
            # ONLY CHANGE: Swapping the contains() logic for your new primary_type_for_deck col
            subset = df[df['primary_type_for_deck'] == t]
            
            label = f"{t}s"
            key = f"df_{current_deck_id}_{t}"

            if not subset.empty:
                st.markdown(f"#### {label} ({int(subset['qty'].sum())})")
                display_df = subset[['qty', 'name', 'code', 'mana', 'total_cards_value', 'status', 'image_url', 'edition']].sort_values("name")
                
                event = st.dataframe(
                    display_df, use_container_width=True, hide_index=True,
                    on_select="rerun", selection_mode="single-row", key=key,
                    column_config={
                        "image_url": None,
                        "edition": None,
                        "qty": st.column_config.NumberColumn(width=35),
                        "status": st.column_config.TextColumn("Coll.", width=55),
                        "total_cards_value": st.column_config.NumberColumn("Value", format="$ %.2f", width=50)
                    }
                )

                if event.selection.rows:
                    new_selection = display_df.iloc[event.selection.rows[0]]
                    current_selection = st.session_state.get('selected_card')
                    if current_selection is None or current_selection['code'] != new_selection['code']:
                        st.session_state.selected_card = new_selection
                        st.rerun()

    # Render top grid
    for type in left_types: draw_type_table(mainboard, type, col_left)
    for type in right_types: draw_type_table(mainboard, type, col_right)

    
    col_img, col_side = st.columns([1, 2], gap="large")

    with col_img:

        st.markdown("#### Card Preview")

        selected = st.session_state.get('selected_card')

        with st.container(border=True):

            if selected is not None:
                img_url = selected['image_url'] if pd.notna(selected['image_url']) else "https://static.wikia.nocookie.net/mtgsalvation_gamepedia/images/f/f8/Magic_card_back.jpg"
                st.markdown('<div class="centered-preview">', unsafe_allow_html=True)
                st.image(img_url, width=280)
                st.markdown(
                    f"""<h4 style='font-size: 21px; font-weight: 600;'>{selected['name']}   <span style='font-size: 17px;color: #7f8c8d;'>{selected['edition']}</span></h4>
                    """, 
                    unsafe_allow_html=True
                )
                st.markdown('</div>', unsafe_allow_html=True)
                
            else:
                st.markdown('<div class="centered-preview">', unsafe_allow_html=True)
                st.info("Select a card to view.")
                st.image("https://static.wikia.nocookie.net/mtgsalvation_gamepedia/images/f/f8/Magic_card_back.jpg", width=280)
                st.markdown('</div>', unsafe_allow_html=True)

    with col_side:

        if not sideboard.empty:
            cards_side = sideboard['qty'].sum()
            value_side = sideboard['total_cards_value'].sum()
            side_pct = (sideboard['num_for_deck'].sum() / cards_side * 100) if cards_side > 0 else 0
            
            st.markdown(f"""
                <div style="margin-top:-15px; margin-bottom:15px; text-align: right;">
                    <div style="font-size:26px; font-weight:500; margin-bottom:5px;">Sideboard ({int(cards_side)}) ~ ${value_side:,.2f}</div>
                    <div style="display: flex; align-items: center; justify-content: flex-end; gap: 7px;">
                        <p style="margin-left: 10px; margin-bottom: 0; font-size: 12px;">{side_pct:.1f}%</p>
                        <div style="background-color: #e0e0e0; border-radius: 5px; width: 210px; height: 8px;">
                            <div style="background-color: #34495e; width: {side_pct}%; height: 8px; border-radius: 5px;"></div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            side_display = sideboard[['qty', 'name', 'code', 'mana', 'total_cards_value', 'status', 'image_url', 'rarity', 'edition']].sort_values("name")
            
            side_event = st.dataframe(
                side_display, use_container_width=True, hide_index=True,
                on_select="rerun", selection_mode="single-row", key=f"side_{current_deck_id}",
                column_config={
                    "image_url": None,
                    "rarity": None,
                    "edition": None,
                    "qty": st.column_config.NumberColumn(width=35),
                    "status": st.column_config.TextColumn("Coll.", width=55),
                    "total_cards_value": st.column_config.NumberColumn("Value", format="$ %.2f", width=50)
                }
            )
            if side_event.selection.rows:
                new_sel = side_display.iloc[side_event.selection.rows[0]]
                st.session_state.selected_card = new_sel
                st.rerun()


def render_deck_stats_view(deck_cards):

    # --- ROW 1: SUMMARY TABLE & TOP SETS ---
    row_1_col_left, row_1_col_right = st.columns([1, 1], gap="small")
    
    # LEFT COLUMN: Summary Table (pass for now)
    with row_1_col_left:
        with st.container(border=True):
            st.markdown("<h3 style='margin: 0; margin-bottom: 10px;'>Summary</h3>", unsafe_allow_html=True)
            st.info("Summary table coming soon")

    # RIGHT COLUMN: Top Sets Donut
    with row_1_col_right:
        with st.container(border=True):
            st.markdown("<h3 style='margin: 0; margin-bottom: 10px;'>Top Sets</h3>", unsafe_allow_html=True)
            
            # Section filter for sets
            section_mode_sets = st.radio(
                "Section:",
                ["Main", "Side", "Both"],
                horizontal=True,
                key="deck_sets_section"
            )
            
            sort_metric_sets = st.radio(
                "Rank by:",
                ["Qty", "Val"],
                horizontal=True,
                key="deck_sets_sort"
            )
            
            # Filter by section first
            df_to_use = deck_cards.copy()
            if section_mode_sets != "Both":
                section_val = "main" if section_mode_sets == "Main" else "sideboard"
                df_to_use = df_to_use[df_to_use['section'].str.lower() == section_val]

            # Then aggregate
            set_data = features.get_top_sets_aggregate(df_to_use)
            fig_sets = features.get_top_sets_donut(set_data, sort_metric_sets)
            
            if fig_sets:
                st.plotly_chart(fig_sets, use_container_width=True, key="deck_sets_plot")
            else:
                st.info("No sets in this section.")
    
    st.divider()
    
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
                sel_r = st.multiselect("Filter Rarity:", options=dynamic_rarities, key="ds_rarity")
            
            with c2:
                deck_section_mode = st.radio("Section:", ["Main", "Side", "Both"], horizontal=True, key="ds_view")

            # --- CALLER FILTERS THE DF ---
            df_to_use = deck_cards.copy()
            
            # Handle section filter
            if deck_section_mode != "Both":
                section_val = "main" if deck_section_mode == "Main" else "sideboard"
                df_to_use = df_to_use[df_to_use['section'].str.lower() == section_val]
            
            # Handle rarity filter
            if sel_r:
                rarity_map = {'Common': 'Common', 'Uncommon': 'Uncommon', 'Rare': 'Rare', 'Mythic': 'MythicRare'}
                df_to_use = df_to_use[df_to_use['rarity'].isin([rarity_map[r] for r in sel_r])]

            # --- AGGREGATE AND RENDER ---
            df_colors_agg, grand_total = features.get_color_saturation_aggregate(df_to_use)
            fig_color = features.get_color_saturation_widget(df_colors_agg, grand_total, is_trans)
            
            if fig_color:
                st.plotly_chart(fig_color, use_container_width=True, key="ds_color_plot")
            else:
                st.info("No cards match the selected filters.")

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
                ds_section = st.radio("Section:", ["Main", "Side", "Both"], horizontal=True, key="ds_type_sec")

            # --- CALLER FILTERS THE DF ---
            df_to_use = deck_cards.copy()
            
            # Handle section filter
            if ds_section != "Both":
                section_val = "main" if ds_section == "Main" else "sideboard"
                df_to_use = df_to_use[df_to_use['section'].str.lower() == section_val]
            
            # Handle color filter
            if sel_c:
                ui_to_db = {'White': 'W', 'Blue': 'U', 'Black': 'B', 'Red': 'R', 'Green': 'G', 'Colorless': 'C'}
                codes = [ui_to_db[c] for c in sel_c if c in ui_to_db]
                wants_multi = 'Multicolor' in sel_c
                pattern = '|'.join(codes) if codes else None
                mask = df_to_use['color'].str.contains(pattern, na=False) if pattern else pd.Series(False, index=df_to_use.index)
                if wants_multi:
                    mask = mask | (df_to_use['is_multi_colored'] == True)
                df_to_use = df_to_use[mask]

            # --- AGGREGATE AND RENDER ---
            type_data = features.get_type_distribution_aggregate(df_to_use)
            fig_type = features.get_type_distribution_widget(type_data)

            if fig_type:
                st.plotly_chart(fig_type, use_container_width=True, key="ds_type_plot")
            else:
                st.info("No cards match the selected filters.")

    # ROW 3: TOP SETS (Full Width or Column based on your preference)
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

        # --- CALLER FILTERS THE DF ---
        df_to_use = deck_cards.copy()
        
        # Filter by type
        if type_select:
            df_to_use = df_to_use[df_to_use['primary_type_for_deck'].isin(type_select)]
        
        # Filter by color
        if color_select:
            ui_to_db = {'White':'W', 'Blue':'U', 'Black':'B', 'Red':'R', 'Green':'G', 'Colorless':'C'}
            codes = [ui_to_db[c] for c in color_select if c in ui_to_db]
            pattern = '|'.join(codes)
            df_to_use = df_to_use[df_to_use['color'].str.contains(pattern, na=False)]

        # --- AGGREGATE AND RENDER ---
        curve_data = features.get_mana_curve_aggregate(df_to_use)
        fig_cmc = features.get_mana_curve_widget(curve_data, 'Deck View', is_trans)

        if fig_cmc:
            st.plotly_chart(fig_cmc, use_container_width=True, config={'displayModeBar': False}, key="ds_cmc_chart")
        else:
            st.info("No cards match these filters...")

    return


def render_test_deck_view(deck_cards):
    # 1. Prepare Deck
    mainboard = deck_cards[deck_cards['section'].str.contains('main', case=False, na=False)].copy()
    full_deck_df = mainboard.loc[mainboard.index.repeat(mainboard['qty'])].drop(columns=['qty'])

    # 2. State Management
    if 'shuffled_library' not in st.session_state:
        st.session_state.shuffled_library = full_deck_df.sample(frac=1)
        st.session_state.hand = pd.DataFrame()
        st.session_state.ptr = 0
        st.session_state.draw_counter = 0 

    # 3. Corrected Draw Logic (Descending Order)
    def draw(n):
        available = len(st.session_state.shuffled_library) - st.session_state.ptr
        num = min(n, available)
        if num <= 0: return

        new_draw = st.session_state.shuffled_library.iloc[st.session_state.ptr : st.session_state.ptr + num].copy()
        
        # Increment index based on draw order
        new_indices = range(st.session_state.draw_counter + 1, st.session_state.draw_counter + num + 1)
        new_draw.index = new_indices
        
        # Newest cards on top
        st.session_state.hand = pd.concat([new_draw, st.session_state.hand]).sort_index(ascending=False)
        st.session_state.draw_counter += num
        st.session_state.ptr += num

    # --- INITIALIZE SELECTION TO PREVENT CRASH ---
    selection = {"selection": {"rows": []}}

    # --- LAYOUT ---
    interact_col, card_view_col, curve_col = st.columns([1.2, 1, 1.2])

    with interact_col:
        st.subheader("Your Hand")
        c1, c2 = st.columns(2)
        if c1.button("Draw 7 (New)"):
            st.session_state.shuffled_library = full_deck_df.sample(frac=1)
            st.session_state.hand = pd.DataFrame()
            st.session_state.ptr = 0
            st.session_state.draw_counter = 0
            draw(7)
            st.rerun() # Refresh to update UI immediately
            
        if c2.button("Draw 1"):
            draw(1)
            st.rerun()

        if not st.session_state.hand.empty:
            # Overwrite the empty selection with the actual UI component
            selection = st.dataframe(
                st.session_state.hand[['name', 'mana']], 
                on_select="rerun", 
                selection_mode="single-row",
                key="hand_selector",
                hide_index=False,
                use_container_width=True
            )


    with card_view_col:

        st.subheader("Card Preview")
        selected_rows = selection.get("selection", {}).get("rows", [])
        
        if selected_rows and not st.session_state.hand.empty:
            idx_pos = selected_rows[0]
            selected_card = st.session_state.hand.iloc[idx_pos]
            
            # Use your existing image/URL logic
            img_url = selected_card.get('image_url', "https://placehold.co/488x680?text=MTG+Card")
            st.image(img_url, use_container_width=True)
            st.write(f"**{selected_card['name']}**")
            st.caption(f"Draw Order: {selected_card.name}")
        else:
            st.info("Select a card in your hand to preview.")

    with curve_col:
        st.subheader("Hand Curve")
        if not st.session_state.hand.empty:
            # 1. We prepare a temporary 'qty' column because the hand DF has 1 row per card
            hand_to_plot = st.session_state.hand.copy()
            hand_to_plot['qty'] = 1 
            
            # Caller prepares the DF (already filtered to just the hand cards)
            curve_data = features.get_mana_curve_aggregate(hand_to_plot)
            fig_hand = features.get_mana_curve_widget(curve_data, 'Deck Test', is_transposed=True)

            if fig_hand:
                st.plotly_chart(
                    fig_hand, 
                    use_container_width=True, 
                    config={'displayModeBar': False},
                    key="hand_cmc_chart"
                )
            else:
                st.info("No cards in hand to display.")



