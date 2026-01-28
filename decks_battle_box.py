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
    # 1. Inject CSS for progress bars
    st.markdown("""
        <style>
        /* Target only the paragraph tags inside your deck cards */
        [data-testid="stVerticalBlockBorderWrapper"] p {
            margin-bottom: 0px !important;
            padding-bottom: 2px;
        }
        .pb-bg { 
            width: 100%; 
            background-color: #262730; 
            border-radius: 2px; 
            height: 8px; 
            margin-bottom: 4px; /* Reduced margin */
            margin-top: 2px; 
        }
        .pb-fill { height: 8px; border-radius: 2px; transition: width 0.4s ease; }
        </style>
        """, unsafe_allow_html=True)

    # 2. Filter Logic
    col_s, _ = st.columns([1, 2])
    with col_s:
        filter_type = st.select_slider("Filter Decks", options=["Meta", "My Brews"])
    
    target_val = "Brew" if filter_type == "My Brews" else "Meta"
    if 'Brew' not in df_battle_box.columns:
        df_battle_box['Brew'] = 'Meta'
        
    filtered_df = df_battle_box[df_battle_box['Brew'] == target_val].sort_values("Priority")
    
    # --- THE MISSING LINE ---
    decks = filtered_df['DeckName'].unique()

    if len(decks) == 0:
        st.info(f"No decks categorized as {filter_type} found.")
        return

    # 3. Grid Rendering
    for i in range(0, len(decks), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(decks):
                deck_name = decks[i + j]
                deck_data = filtered_df[filtered_df['DeckName'] == deck_name].iloc[0]
                
                # Stats & Dynamic Colors
                # Note: These columns must exist in your DB from the build_db.py update
                m_pct = int(deck_data.get('CompletionPct', 0))
                s_pct = int(deck_data.get('SideboardPct', 0))
                m_color = "#00CC66" if m_pct >= 100 else "#FF4B4B"
                s_color = "#00CC66" if s_pct >= 100 else "#FFA500"

                # Image Processing
                img_url = deck_data['bb_deck_img'] if pd.notna(deck_data['bb_deck_img']) else CARD_BACK_URL
                tile = create_deck_tile(img_url)
                img_src = f"data:image/png;base64,{img_to_bytes(tile)}" if tile else CARD_BACK_URL

                with cols[j]:
                    with st.container(border=True):
                        # Use columns for internal tile layout: Text/Bars (left) | Image (right)
                        c_text, c_img = st.columns([1.8, 1])
                        
                        with c_text:
                            st.markdown(f"**{deck_name}**")
                            
                            # Mainboard Section
                            st.caption(f"Main: {m_pct}%")
                            st.markdown(f'<div class="pb-bg"><div class="pb-fill" style="width:{m_pct}%; background-color:{m_color};"></div></div>', unsafe_allow_html=True)
                            
                            # Sideboard Section
                            st.caption(f"Side: {s_pct}%")
                            st.markdown(f'<div class="pb-bg"><div class="pb-fill" style="width:{s_pct}%; background-color:{s_color};"></div></div>', unsafe_allow_html=True)

                        with c_img:
                            st.markdown(f'<img src="{img_src}" style="width:100%; border-radius:4px; border:1px solid #444; margin-top:10px;">', unsafe_allow_html=True)
                        
                        st.write("") # Spacer
                        if st.button("View Details", key=f"btn_{deck_name}", use_container_width=True):
                            st.session_state.view = f"deck_{deck_name}"
                            st.rerun()


def render_decks_menu(df_battle_box):
    render_battle_box_gallery(df_battle_box)

def render_decks_view(df_inventory, df_all_decks):
    current_view = st.session_state.get("view", "")
    deck_name = current_view.replace("deck_", "")
    render_deck_detail(deck_name, df_inventory, df_all_decks)