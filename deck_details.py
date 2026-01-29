import streamlit as st
import pandas as pd

def render_deck_detail(deck_name, df_inventory, df_all_decks, df_battle_box):
    # --- ROW 1: HEADER & NAVIGATION ---
    c1, c2 = st.columns([2, 1], gap="medium", vertical_alignment="center")

    with c1:
        st.title(f"{deck_name}")
        deck_view_mode = st.radio(
            "Select View:",
            ["Deck", "Analysis", "Test"],
            horizontal=True,
            label_visibility="collapsed"
        )

    with c2:
        if st.button("⬅ Back", use_container_width=True):
            st.session_state.view = "battle_box"
            st.rerun()

    st.divider()

    # --- VIEW ROUTING ---
    if deck_view_mode == "Deck":
        render_deck_list_view(deck_name, df_inventory, df_all_decks, df_battle_box)
    elif deck_view_mode == "Analysis":
        st.info("Analysis View - Coming next")
    elif deck_view_mode == "Test":
        st.info("Test View - Coming next")

def render_deck_list_view(deck_name, df_inventory, df_all_decks, df_battle_box):
    # 1. Filter Data
    deck_cards = df_all_decks[df_all_decks['DeckName'] == deck_name].copy()
    
    if deck_cards.empty:
        st.error("Deck data not found.")
        return

    # 2. Status Logic (using your exact col names)
    deck_cards['status'] = deck_cards.apply(
        lambda x: "✅" if x['num_for_deck'] >= x['qty'] else f"❌ ({int(x['num_for_deck'])}/{int(x['qty'])})", 
        axis=1
    )

    # 3. Separate Main vs Side
    mainboard = deck_cards[deck_cards['section'].str.contains('Main', case=False, na=False)]
    sideboard = deck_cards[deck_cards['section'].str.contains('Side', case=False, na=False)]

    # 4. Mainboard Layout (Wrapped by Type)
    col_left, col_right = st.columns(2, gap="large")
    
    left_types = ['Creature', 'Instant', 'Sorcery']
    right_types = ['Enchantment', 'Artifact', 'Land']

    def draw_type_groups(df, types, ui_col):
        with ui_col:
            for t in types:
                # Subset using lowercase 'type'
                subset = df[df['type'].str.contains(t, case=False, na=False)]
                if not subset.empty:
                    st.markdown(f"#### {t}s ({int(subset['qty'].sum())})")
                    st.dataframe(
                        subset[['status', 'qty', 'name', 'mana']].sort_values("name"),
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "status": st.column_config.TextColumn("", width=45),
                            "qty": st.column_config.NumberColumn("Qty", format="%d", width=35),
                            "name": st.column_config.TextColumn("Name"),
                            "mana": st.column_config.TextColumn("Cost", width=60)
                        }
                    )

    draw_type_groups(mainboard, left_types, col_left)
    draw_type_groups(mainboard, right_types, col_right)

    # 5. Sideboard (Full width below)
    if not sideboard.empty:
        st.divider()
        st.markdown(f"### Sideboard ({int(sideboard['qty'].sum())})")
        st.dataframe(
            sideboard[['status', 'qty', 'name', 'type', 'mana']].sort_values("name"),
            use_container_width=True,
            hide_index=True,
            column_config={
                "status": st.column_config.TextColumn("", width=45),
                "qty": st.column_config.NumberColumn("Qty", format="%d", width=35),
                "name": st.column_config.TextColumn("Name"),
                "type": st.column_config.TextColumn("Type"),
                "mana": st.column_config.TextColumn("Cost", width=60)
            }
        )