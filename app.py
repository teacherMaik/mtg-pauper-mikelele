import streamlit as st
import pandas as pd
import features 
import plotly.express as px
from data_manager import load_inventory, load_all_decks

# Ensure these function names match exactly what is inside decks_battle_box.py
from decks_battle_box import (
    render_decks_menu,  # This will likely be your Gallery logic
    render_decks_view   # This is your detailed [1.5, 1] layout
)

from inventory_full import render_inventory_stats_view
from inventory_search import render_card_search_view

st.set_page_config(page_title="MTG Pauper Playground", layout="wide")

# Load data
df_inventory, last_update = load_inventory()
df_all_decks = load_all_decks()

# 1. INITIALIZATION
if "view" not in st.session_state:
    st.session_state.view = "battle_box" 
if "selected_card_name" not in st.session_state:
    st.session_state.selected_card_name = None

# 2. SIDEBAR NAVIGATION (Your code is perfect here)
with st.sidebar:
    st.header('Decks')
    current_view = st.session_state.get("view", "")
    
    # UI Highlight Logic: Active if in any deck-related view
    # We use .get() to avoid errors if the key is missing
    current_view = st.session_state.get("view", "")
    deck_active = current_view in ["battle_box", "battle_box_stats", "test-deck"] or current_view.startswith("deck_")

    if st.button("My Battle Box", use_container_width=True, 
                 type="primary" if current_view == "battle_box" else "secondary"):
        st.session_state.view = "battle_box"
        st.rerun()

    if st.button("Deck Stats", use_container_width=True, 
                 type="primary" if current_view == "battle_box_stats" else "secondary"):
        st.session_state.view = "battle_box_stats"
        st.rerun()

    if st.button("Play Around", use_container_width=True, 
                 type="primary" if current_view == "test-deck" else "secondary"):
        st.session_state.view = "test-deck"
        st.rerun()

    st.divider()
    st.header("Collection")

    if st.button("Inventory Stats", use_container_width=True, 
                 type="primary" if current_view == "inventory_stats" else "secondary"):
        st.session_state.view = "inventory_stats"
        st.rerun()

    if st.button("Search Cards", use_container_width=True, 
                 type="primary" if current_view == "inventory_search" else "secondary"):
        st.session_state.view = "inventory_search"
        st.rerun()

st.title("Mikelele's Pauper Playground")
st.caption(f"*Last update on {last_update}*")

# 3. MAIN CONTENT ROUTER
# Syncing the names called here with the names imported above
if st.session_state.view == "battle_box":
    # Calling the Gallery function from your component
    render_decks_menu(df_inventory, df_all_decks)
    
elif st.session_state.view == "battle_box_stats":
    st.write("### Battle Box Overview")
    # render_battle_box_overview(df_all_decks) # Define this in a component

elif st.session_state.view == "test-deck":
    st.write("### Draw Machine")
    # render_play_around(df_all_decks) # Define this in a component
    
elif st.session_state.view.startswith("deck_"):
    # Pass the variables to your detailed layout
    render_decks_view(df_inventory, df_all_decks)

elif st.session_state.view == "inventory_stats":
    render_inventory_stats_view(df_inventory, df_all_decks)

elif st.session_state.view == "inventory_search":
    render_card_search_view(df_inventory, df_all_decks)