import streamlit as st
import pandas as pd
import features  # Your new file
import plotly.express as px
from data_manager import load_inventory, load_all_decks
from inventory_view import render_inventory_view
from decks_view import render_decks_view

st.set_page_config(page_title="MTG Pauper Playground", layout="wide")

df_inventory, last_update = load_inventory()
df_all_decks = load_all_decks()

if 'view' not in st.session_state:
    st.session_state.view = "inventory"

with st.sidebar:
    st.header("Play Around")
    color_data, type_data = features.get_sidebar_stats(df_inventory)

    # Navigation (Same as yours)
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

    # --- SECTION 1: STATS TABLE (STAYS ON TOP) ---
    st.subheader("Collection Stats")
    total_qty = df_inventory['Qty'].sum()
    total_val = df_inventory['Total'].sum()
    total_decks = df_all_decks['DeckName'].nunique() if not df_all_decks.empty else 0

    summary_df = pd.DataFrame({
        "Summary": ["Total Cards", "Total Value", "Total Decks"],
        "Stats": [f"{total_qty:,}", f"${total_val:,.2f}", f"{total_decks}"]
    })
    st.dataframe(summary_df, use_container_width=True, hide_index=True)

    # --- SECTION 2: COLOR IDENTITY PIE CHART ---
    if not color_data.empty:
        color_map = {
            'White': '#F0F0F0', 'Blue': '#0000FF', 'Black': '#000000',
            'Red': '#FF0000', 'Green': '#008000', 'Colorless': '#90ADBB'
        }

        fig = px.pie(
            color_data, 
            values='Count', 
            names='Color',
            color='Color',
            color_discrete_map=color_map,
            hole=0.4
        )

        # FIXED: Pass the array directly to customdata to prevent NaN
        fig.update_traces(
            customdata=color_data['Value'],
            hovertemplate="<b>%{label}</b><br>Pips: %{value}<br>Value: $%{customdata:,.2f}<extra></extra>",
            textinfo='none',
            # THIS ADDS THE SLICE BORDERS
            marker=dict(line=dict(color='#444444', width=1.5)) 
        )

        fig.update_layout(
            showlegend=False, 
            height=220, 
            margin=dict(l=10, r=10, t=10, b=10)
        )

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # --- SECTION 3: TYPE DISTRIBUTION (BELOW PIE) ---
    if not type_data.empty:
        # Create a horizontal bar chart
        fig_bar = px.bar(
            type_data,
            x='Count',
            y='Type',
            orientation='h',
            text_auto=True # Shows the number inside the bar
        )

        fig_bar.update_traces(
            marker_color="#ED72F1", # Clean blue color
            marker_line=dict(color='#000000', width=1),
            hovertemplate="<b>%{y}</b><br>Total: %{x}<extra></extra>"
        )

        fig_bar.update_layout(
            height=250,
            margin=dict(l=10, r=10, t=10, b=10),
            xaxis_title=None,
            yaxis_title=None,
            # Remove gridlines for a cleaner sidebar look
            xaxis=dict(showgrid=False, showticklabels=False),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )


        st.plotly_chart(fig_bar, use_container_width=True, config={'displayModeBar': False})

st.title("Mikelele's Pauper Playground")

if st.session_state.view == "inventory":
    render_inventory_view(df_inventory, df_all_decks, last_update)
elif st.session_state.view == "decks_menu":
    render_decks_view(df_inventory, df_all_decks)
## elif st.session_state.view.startswith("deck_"):
##    deck_name = st.session_state.view.replace("deck_", "")
##    render_deck_detail(deck_name)