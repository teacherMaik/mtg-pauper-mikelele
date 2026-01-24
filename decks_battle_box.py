import streamlit as st
import pandas as pd
import requests
import base64
from io import BytesIO
from PIL import Image
from deck_details import render_deck_detail

CARD_BACK_URL = "https://gamepedia.cursecdn.com/mtgsalvation_gamepedia/f/f8/Magic_card_back.jpg"

# --- HELPERS ---
def img_to_bytes(img):
    buf = BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()

@st.cache_data(show_spinner=False)
def create_deck_tile(url, opacity=1.0):
    try:
        response = requests.get(url, timeout=5)
        img = Image.open(BytesIO(response.content)).convert("RGBA")
        img.thumbnail((300, 300))
        return img
    except Exception:
        return None

# --- GALLERY VIEW ---
def render_battle_box_gallery(df_battle_box):
    st.markdown("""
        <style>
        /* Progress Bar Styling */
        .pb-bg {
            width: 100%;
            background-color: #262730;
            border-radius: 2px;
            height: 6px;
            margin-top: 8px;
        }
        .pb-fill {
            height: 6px;
            border-radius: 2px;
            transition: width 0.4s ease;
        }
        /* Standardizing container height so buttons align */
        [data-testid="stVerticalBlockBorderWrapper"] {
            min-height: 220px;
        }
        </style>
    """, unsafe_allow_html=True)

    # Filtering Logic
    col_s, _ = st.columns([1, 3])
    with col_s:
        filter_type = st.select_slider("Filter Decks", options=["Meta", "My Brews"])
    
    target_val = "Brew" if filter_type == "My Brews" else "Meta"
    # Ensure column exists
    if 'Brew' not in df_battle_box.columns:
        df_battle_box['Brew'] = 'Meta'
        
    filtered_df = df_battle_box[df_battle_box['Brew'] == target_val].sort_values("Priority")
    decks = filtered_df['DeckName'].unique()

    if len(decks) == 0:
        st.info(f"No decks categorized as {filter_type} found.")
        return

    # Grid Rendering
    for i in range(0, len(decks), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(decks):
                deck_name = decks[i + j]
                deck_data = filtered_df[filtered_df['DeckName'] == deck_name].iloc[0]
                
                img_url = deck_data['Thumbnail'] if pd.notna(deck_data['Thumbnail']) else CARD_BACK_URL
                pct = int(deck_data.get('CompletionPct', 0))
                bar_color = "#ff4b4b" if pct < 50 else "#ffa500" if pct < 100 else "#00cc66"
                
                with cols[j]:
                    with st.container(border=True):
                        tile = create_deck_tile(img_url)
                        img_src = f"data:image/png;base64,{img_to_bytes(tile)}" if tile else CARD_BACK_URL

                        # THE ROW: Name + Bar (Left) | Image (Right)
                        st.markdown(f"""
                            <div style="display: flex; gap: 12px; align-items: flex-start; min-height: 120px;">
                                <div style="flex-grow: 1;">
                                    <div style="font-weight: bold; font-size: 1.15rem; line-height: 1.2; margin-bottom: 4px;">
                                        {deck_name}
                                    </div>
                                    <div style="font-size: 0.8rem; color: #888;">{pct}% Complete (Main)</div>
                                    <div class="pb-bg">
                                        <div class="pb-fill" style="width: {pct}%; background-color: {bar_color};"></div>
                                    </div>
                                </div>
                                <div style="flex-shrink: 0;">
                                    <img src="{img_src}" style="width: 85px; height: 115px; object-fit: cover; border: 1px solid #444;">
                                </div>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        st.write("") # Spacer
                        if st.button(f"View Deck", key=f"btn_{deck_name}", use_container_width=True):
                            st.session_state.view = f"deck_{deck_name}"
                            st.rerun()

def render_decks_menu(df_battle_box):
    render_battle_box_gallery(df_battle_box)

def render_decks_view(df_inventory, df_all_decks):
    current_view = st.session_state.get("view", "")
    deck_name = current_view.replace("deck_", "")
    render_deck_detail(deck_name, df_inventory, df_all_decks)