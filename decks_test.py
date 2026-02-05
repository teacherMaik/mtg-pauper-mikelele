import pandas as pd
import streamlit as st

def render_test_deck_view(deck_cards):
    mainboard = deck_cards[deck_cards['section'].str.contains('Main', case=False, na=False)].copy()
    
    # 1. Explode and convert to List of Lists
    # We select only the columns we need (e.g., Name and Mana Cost)
    full_deck_list = (
        mainboard.loc[mainboard.index.repeat(mainboard['qty'])]
        .drop(columns=['qty'])
        [['name', 'mana_cost']] # Select your desired columns
        .values.tolist()        # Convert to [[name, mana], [name, mana]...]
    )

    # 2. Shuffle (using standard Python random)
    import random
    if 'shuffled_list' not in st.session_state:
        random.shuffle(full_deck_list)
        st.session_state.shuffled_list = full_deck_list
        st.session_state.pointer = 0

    # 3. Splicing for the draw
    def draw_next(n):
        start = st.session_state.pointer
        end = start + n
        new_cards = st.session_state.shuffled_list[start:end]
        
        if 'hand_list' not in st.session_state:
            st.session_state.hand_list = []
            
        st.session_state.hand_list.extend(new_cards)
        st.session_state.pointer = end

    # --- UI Example ---
    if st.button("Draw 7"):
        # Reset and Shuffle
        random.shuffle(full_deck_list)
        st.session_state.shuffled_list = full_deck_list
        st.session_state.hand_list = []
        st.session_state.pointer = 0
        draw_next(7)

    # Displaying the list of lists in a way that looks good
    if 'hand_list' in st.session_state and st.session_state.hand_list:
        # Convert back to DF just for the clean Streamlit UI
        hand_df = pd.DataFrame(st.session_state.hand_list, columns=['Name', 'Mana'])
        st.table(hand_df)