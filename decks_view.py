import streamlit as st
import pandas as pd
import os

def render_decks_menu(df_all_decks):
    st.subheader("Explore Your Decks")
    t_col1, t_col2, t_col3 = st.columns([8, 84, 8])
    with t_col2:
        if not df_all_decks:
            st.warning("No deck CSVs found.")
        else:
            for deck in df_all_decks:
                if st.button(f"📂 {deck}", key=f"btn_{deck}", use_container_width=True):
                    st.session_state.view = f"deck_{deck}"
                    st.rerun()

def render_deck_detail(deck_name):
    if st.button("⬅️ Back to Decks"):
        st.session_state.view = "decks_menu"
        st.rerun()
    
    st.subheader(f"Decklist: {deck_name}")
    t_col2 = st.columns([8, 84, 8])[1]
    with t_col2:
        try:
            # Look inside the subfolder
            path = os.path.join("data", "decks", deck_name)
            df_deck = pd.read_csv(path)
            st.dataframe(df_deck, use_container_width=True, hide_index=True)
        except Exception as e:
            st.error(f"Error loading {deck_name}: {e}")