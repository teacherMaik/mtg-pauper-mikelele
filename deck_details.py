import streamlit as st
import pandas as pd

def render_deck_detail(deck_name, df_inventory, df_all_decks):
    # 1. HEADER & NAVIGATION
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(f"📊 {deck_name}")
    with col2:
        if st.button("⬅ Back", use_container_width=True):
            st.session_state.view = "battle_box"
            st.rerun()

    # 2. DATA FILTERING
    # Ensure case-insensitive match for the deck name
    deck_cards = df_all_decks[df_all_decks['DeckName'].str.lower() == deck_name.lower()].copy()
    
    if deck_cards.empty:
        st.error(f"Could not find card data for '{deck_name}'")
        st.info("Check if the DeckName in the database matches the filename prefix.")
        return

    # Filter for Mainboard only
    main_board = deck_cards[deck_cards['Section'].str.contains('Main', case=False, na=False)].copy()
    
    # 3. ACQUISITION LOGIC (Live check against inventory)
    # We group inventory by Name to see what we have available
    inv_pool = df_inventory.groupby('Name')['Qty'].sum().to_dict()
    
    def check_owned(row):
        return inv_pool.get(row['Name'], 0)

    main_board['Owned'] = main_board.apply(check_owned, axis=1)
    main_board['Status'] = main_board.apply(
        lambda x: "✅" if x['Owned'] >= x['Qty'] else f"❌ ({x['Owned']}/{x['Qty']})", axis=1
    )

    # 4. STATS METRICS
    total_needed = main_board['Qty'].sum()
    total_owned = main_board.apply(lambda x: min(x['Qty'], x['Owned']), axis=1).sum()
    completion = int((total_owned / total_needed) * 100) if total_needed > 0 else 0

    m1, m2, m3 = st.columns(3)
    m1.metric("Mainboard Completion", f"{completion}%")
    m2.metric("Cards Owned", f"{int(total_owned)}")
    m3.metric("Total Required", f"{int(total_needed)}")

    st.divider()

    # 5. CARD TABLE
    st.subheader("Card List")
    # Sort so missing cards are at the top
    main_board = main_board.sort_values(by="Owned", ascending=True)
    
    st.dataframe(
        main_board[['Status', 'Qty', 'Name', 'Mana', 'Type']],
        use_container_width=True,
        hide_index=True,
        column_config={
            "Qty": st.column_config.NumberColumn("Required"),
            "Status": st.column_config.TextColumn("Availability"),
            "Mana": st.column_config.TextColumn("Cost")
        }
    )

    # Optional: Sideboard section if you want to see it but not count it
    side_board = deck_cards[deck_cards['Section'].str.contains('Side', case=False, na=False)]
    if not side_board.empty:
        with st.expander("View Sideboard (Not included in completion %)"):
            st.table(side_board[['Qty', 'Name']])