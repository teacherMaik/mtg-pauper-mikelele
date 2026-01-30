## app.py

import streamlit as st
import pandas as pd
from data_manager import load_inventory, load_all_decks, load_battle_box

# --- COMPONENT IMPORTS ---
from decks_battle_box import render_decks_menu, render_decks_view
from decks_stats import render_bb_stats_view
from deck_details import render_deck_detail
from inventory_full import render_inventory_stats_view
from inventory_search import render_card_search_view


st.set_page_config(page_title="MTG Pauper Playground", layout="wide")

# --- DATA LOADING ---
df_inventory, last_update = load_inventory()
df_all_decks = load_all_decks()
df_battle_box = load_battle_box()

if "view" not in st.session_state:
    st.session_state.view = "battle_box" 

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    current_view = st.session_state.view
    st.header('Decks')
    
    if st.button("My Battle Box", use_container_width=True, 
                 type="primary" if current_view == "battle_box" else "secondary"):
        st.session_state.view = "battle_box"
        st.rerun()

    if st.button("Battle Box Stats", use_container_width=True, 
                 type="primary" if current_view == "battle_box_stats" else "secondary"):
        st.session_state.view = "battle_box_stats"
        st.rerun()

    if st.button("Test a Deck", use_container_width=True, 
                 type="primary" if current_view == "test_deck" else "secondary"):
        st.session_state.view = "test_deck"
        st.rerun()

    st.divider()
    st.header("Collection")

    if st.button("Stats", use_container_width=True, 
                 type="primary" if current_view == "inventory_stats" else "secondary"):
        st.session_state.view = "inventory_stats"
        st.rerun()

    if st.button("Search a Card", use_container_width=True, 
                 type="primary" if current_view == "inventory_search" else "secondary"):
        st.session_state.view = "inventory_search"
        st.rerun()

# --- HEADER ---
if st.session_state.get('view', '').startswith("deck_"):
    # Split header: Title on left, Back button on right
    h_c1, h_c2 = st.columns([4, 1], vertical_alignment="center")
    with h_c1:
        st.title("Mikelele's Pauper Playground")
        st.caption(f"*Last update on {last_update}*")
    with h_c2:
        st.markdown("""
            <style>
            button[kind="secondary"] {
                background-color: #2c3e50 !important;
                color: white !important;
                border: none !important;
            }
            button[kind="secondary"]:hover {
                background-color: #34495e !important;
                color: white !important;
            }
            </style>
        """, unsafe_allow_html=True)

        if st.button("⬅ Battle Box"):
            st.session_state.view = "battle_box"
            st.rerun()
else:
    # Standard view: Full width title
    st.title("Mikelele's Pauper Playground")
    st.caption(f"*Last update on {last_update}*")

# --- ROUTER ---
view = st.session_state.view

if view == "battle_box":
    render_decks_menu(df_battle_box)
elif view.startswith("deck_"):
    # Strip the prefix to get the actual deck name
    deck_name = view.replace("deck_", "")
    # Call the detail view directly or ensure the intermediary has all 3
    render_deck_detail(deck_name, df_inventory, df_all_decks, df_battle_box)
elif view == "battle_box_stats":
    render_bb_stats_view(df_all_decks, df_battle_box)
elif view == "test_deck":
    render_deck_detail("Test Deck", df_inventory, df_all_decks)
elif view == "inventory_stats":
    render_inventory_stats_view(df_inventory, df_all_decks)
elif view == "inventory_search":
    render_card_search_view(df_inventory, df_all_decks)
# ... other views