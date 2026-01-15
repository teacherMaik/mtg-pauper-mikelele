import streamlit as st
import pandas as pd
import features  # Your new file
import plotly.express as px
from data_manager import load_inventory, load_all_decks
from inventory_view import render_inventory_view
from decks_view import render_decks_menu, render_deck_detail

st.set_page_config(page_title="MTG Pauper Playground", layout="wide")

df_inventory = load_inventory()
df_all_decks = load_all_decks()

if 'view' not in st.session_state:
    st.session_state.view = "inventory"

with st.sidebar:
    st.header("Play Around")

    if st.button("Full Collection", use_container_width=True, 
                 type="primary" if st.session_state.view == "inventory" else "secondary"):
        st.session_state.view = "inventory"
        st.rerun()
    
    deck_active = st.session_state.view == "decks_menu" or st.session_state.view.startswith("deck_")
    if st.button("Decks", use_container_width=True, 
                 type="primary" if deck_active else "secondary"):
        st.session_state.view = "decks_menu"
        st.rerun()

    st.divider()

    # 1. Calculate the raw numbers
    total_qty = df_inventory['Qty'].sum()
    total_val = df_inventory['Total'].sum()

    # Count unique deck names from the decks dataframe
    # We use .get() or a check to ensure the df exists and isn't empty
    total_decks = df_all_decks['DeckName'].nunique() if not df_all_decks.empty else 0

    # 2. Create the DataFrame with the 3rd row for Decks
    summary_df = pd.DataFrame({
        "Summary": ["Total Cards", "Total Value", "Total Decks"],
        "Stats": [
            f"{total_qty:,}", 
            f"${total_val:,.2f}", 
            f"{total_decks}" # Plain number for deck count
        ]
    })

    # 3. Display it in the sidebar
    with st.sidebar:
        st.header("Some Stats")
        st.dataframe(
            summary_df, 
            use_container_width=True, 
            hide_index=True
        )

st.title("Mikelele's Pauper Playground")

if st.session_state.view == "inventory":
    render_inventory_view(df_inventory, df_all_decks)
elif st.session_state.view == "decks_menu":
    render_decks_menu(df_all_decks)
elif st.session_state.view.startswith("deck_"):
    deck_name = st.session_state.view.replace("deck_", "")
    render_deck_detail(deck_name)