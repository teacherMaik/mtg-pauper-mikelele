import streamlit as st
import pandas as pd
import os
from data_manager import load_inventory, load_all_decks, load_battle_box

# --- COMPONENT IMPORTS ---
from decks_battle_box import render_decks_menu, render_decks_view
from inventory_full import render_inventory_stats_view
from inventory_search import render_card_search_view

# --- PAGE CONFIG ---
st.set_page_config(page_title="MTG Pauper Playground", layout="wide")

# --- DATA LOADING ---
df_inventory, last_update = load_inventory()
df_all_decks = load_all_decks()
df_battle_box = load_battle_box()

# --- INITIALIZATION ---
if "view" not in st.session_state:
    st.session_state.view = "battle_box" 

# --- SIDEBAR NAVIGATION ---
with st.sidebar:
    current_view = st.session_state.get("view", "")

    st.header('Decks')
    
    # 1. My Battle Box (The Gallery)
    if st.button("My Battle Box", use_container_width=True, 
                 type="primary" if current_view == "battle_box" else "secondary"):
        st.session_state.view = "battle_box"
        st.rerun()

    # 2. Battle Box Stats
    if st.button("Battle Box Stats", use_container_width=True, 
                 type="primary" if current_view == "battle_box_stats" else "secondary"):
        st.session_state.view = "battle_box_stats"
        st.rerun()

    # 3. Test a Deck
    if st.button("Test a Deck", use_container_width=True, 
                 type="primary" if current_view == "test-deck" else "secondary"):
        st.session_state.view = "test-deck"
        st.rerun()

    st.divider()
    st.header("Collection")

    # 4. Inventory Stats
    if st.button("Stats", use_container_width=True, 
                 type="primary" if current_view == "inventory_stats" else "secondary"):
        st.session_state.view = "inventory_stats"
        st.rerun()

    # 5. Search a Card
    if st.button("Search a Card", use_container_width=True, 
                 type="primary" if current_view == "inventory_search" else "secondary"):
        st.session_state.view = "inventory_search"
        st.rerun()

    # Debugging helper (Optional - can be commented out)
    st.divider()
    st.caption(f"DEBUG: {current_view}")

# --- HEADER ---
st.title("Mikelele's Pauper Playground")
st.caption(f"*Last update on {last_update}*")

# --- MAIN CONTENT ROUTER ---
view = st.session_state.view

# Handle Gallery
if view == "battle_box":
    render_decks_menu(df_battle_box)

# Handle Dynamic Deck Detail Views
elif view.startswith("deck_"):
    render_decks_view(df_inventory, df_all_decks)

# Handle Other Sections
elif view == "battle_box_stats":
    st.write("### Battle Box Stats")
    # render_battle_box_stats(df_all_decks, df_battle_box)

elif view == "test-deck":
    st.write("### Draw Machine / Playtesting")
    # render_test_deck_view(df_all_decks)

elif view == "inventory_stats":
    render_inventory_stats_view(df_inventory, df_all_decks)

elif view == "inventory_search":
    render_card_search_view(df_inventory, df_all_decks)

else:
    st.warning("Section not found. Returning to Battle Box.")
    st.session_state.view = "battle_box"
    st.rerun()