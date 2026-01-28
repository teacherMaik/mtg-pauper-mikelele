import streamlit as st
import pandas as pd

def render_deck_detail(deck_name, df_inventory, df_all_decks, df_battle_box):
    # 1. HEADER & NAVIGATION
    col1, col2 = st.columns([4, 1])
    with col1:
        st.title(f"📊 {deck_name}")
    with col2:
        if st.button("⬅ Back", use_container_width=True):
            st.session_state.view = "battle_box"
            st.rerun()

    # 2. PRIORITY-AWARE DATA FILTERING
    # Sort battle box by priority to simulate the 'Global Build'
    priority_list = df_battle_box.sort_values('Priority')['DeckName'].unique().tolist()
    
    # Initialize a virtual inventory pool for this session
    virtual_pool = df_inventory.groupby('MatchName')['Qty'].sum().to_dict()

    # Simulate the build up to the current deck
    for d in priority_list:
        # Get all cards for this specific deck in the priority queue
        d_cards = df_all_decks[df_all_decks['DeckName'] == d]
        
        if d.lower() == deck_name.lower():
            # This is our target deck. 
            # Capture the state of the pool BEFORE this deck consumes it for auditing
            current_deck_cards = d_cards.copy()
            break
        else:
            # Higher priority deck: Subtract its requirements from the global pool
            for _, card in d_cards.iterrows():
                m_name = card.get('MatchName')
                needed = card.get('Qty', 0)
                if m_name in virtual_pool:
                    virtual_pool[m_name] = max(0, virtual_pool[m_name] - needed)

    if 'current_deck_cards' not in locals():
        st.error(f"Deck '{deck_name}' not found in Battle Box priority list.")
        return

    # 3. CALCULATE AVAILABILITY (Main vs Side)
    def calculate_section_status(df_section):
        if df_section.empty:
            return df_section, 0, 0
        
        # Check against what remains in our virtual_pool
        df_section['Owned'] = df_section['MatchName'].apply(lambda x: virtual_pool.get(x, 0))
        
        # Calculate 'Taken' (you can't take more than exists or more than you need)
        # Note: This logic is slightly simplified; in a real build, Main takes before Side.
        df_section['Status'] = df_section.apply(
            lambda x: "✅" if x['Owned'] >= x['Qty'] else f"❌ ({x['Owned']}/{x['Qty']})", axis=1
        )
        
        needed = df_section['Qty'].sum()
        # Actual cards available for this specific deck
        acquired = df_section.apply(lambda x: min(x['Qty'], x['Owned']), axis=1).sum()
        
        # Update pool for the next section (Main consumes before Side)
        for _, row in df_section.iterrows():
            m_name = row['MatchName']
            virtual_pool[m_name] = max(0, virtual_pool.get(m_name, 0) - row['Qty'])
            
        return df_section, acquired, needed

    # Split and process sections
    main_raw = current_deck_cards[current_deck_cards['Section'].str.contains('Main', case=False, na=False)].copy()
    side_raw = current_deck_cards[current_deck_cards['Section'].str.contains('Side', case=False, na=False)].copy()

    main_df, main_acq, main_need = calculate_section_status(main_raw)
    side_df, side_acq, side_need = calculate_section_status(side_raw)

    # 4. STATS METRICS
    m1, m2, m3 = st.columns(3)
    main_pct = int((main_acq / main_need) * 100) if main_need > 0 else 100
    side_pct = int((side_acq / side_need) * 100) if side_need > 0 else 100

    m1.metric("Mainboard", f"{main_pct}%", help="Availability based on Priority Pool")
    m2.metric("Sideboard", f"{side_pct}%")
    m3.metric("Combined Value", f"${current_deck_cards['Total'].sum():.2f}")

    st.divider()

    # 5. UI DISPLAY
    tab1, tab2 = st.tabs(["Mainboard", "Sideboard"])

    with tab1:
        st.dataframe(
            main_df[['Status', 'Qty', 'Name', 'Mana', 'Type']].sort_values("Status"),
            use_container_width=True, hide_index=True
        )

    with tab2:
        if not side_df.empty:
            st.dataframe(
                side_df[['Status', 'Qty', 'Name', 'Type']].sort_values("Status"),
                use_container_width=True, hide_index=True
            )
        else:
            st.info("No sideboard cards defined for this deck.")