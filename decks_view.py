import streamlit as st
import pandas as pd

# Path to the card back placeholder
CARD_BACK_URL = "https://gamepedia.cursecdn.com/mtgsalvation_gamepedia/f/f8/Magic_card_back.jpg"

def render_decks_view(df_inventory, df_all_decks):
    # 1. State Initialization
    if 'deck_selector_key' not in st.session_state:
        st.session_state.deck_selector_key = 0
    if 'selected_card_name' not in st.session_state:
        st.session_state.selected_card_name = None

    # Layout: Top Row [1.5, 1]
    top_col_left, top_col_right = st.columns([1.5, 1], gap="large")

    with top_col_left:
        deck_options = ["Select Deck..."] + sorted(df_all_decks['DeckName'].unique().tolist())
        selected_deck = st.selectbox(
            "Search or Select Deck", 
            options=deck_options,
            key=f"ds_{st.session_state.deck_selector_key}"
        )

    if selected_deck != "Select Deck...":
        # Data Preparation & Global Price Cleaning
        full_deck = df_all_decks[df_all_decks['DeckName'] == selected_deck].copy()
        full_deck['Price'] = pd.to_numeric(
            full_deck['Price'].astype(str).str.replace('$', '').str.replace(',', ''), 
            errors='coerce'
        ).fillna(0.0)
        
        main_df = full_deck[full_deck['Section'].str.lower() == 'main'].copy()
        side_df = full_deck[full_deck['Section'].str.lower() == 'sideboard'].copy()

        with top_col_right:
            st.title(f"{selected_deck}")

        # --- Render Mainboard Tables ---
        with top_col_left:
            st.markdown("### Mainboard")
            sub1, sub2 = st.columns([1, 1], gap="medium")
            
            col1_types = ['Creature', 'Instant', 'Sorcery']
            col2_types = ['Artifact', 'Enchantment', 'Land']

            with sub1:
                for t in col1_types:
                    t_df = main_df[main_df['Type'].str.contains(t, na=False)]
                    if not t_df.empty:
                        render_list_table(t_df, f"{t}s", t, selected_deck)
            
            with sub2:
                for t in col2_types:
                    t_df = main_df[main_df['Type'].str.contains(t, na=False)]
                    if not t_df.empty:
                        render_list_table(t_df, f"{t}s", t, selected_deck)

        # --- Render Sideboard Section (Bottom Row) ---
        st.divider()
        bot_left, bot_right = st.columns([1.5, 1], gap="large")

        with bot_left:
            st.markdown("### Sideboard")
            if not side_df.empty:
                render_list_table(side_df, "Sideboard Cards", "side_list", selected_deck)
            else:
                st.info("No sideboard cards defined.")

        with bot_right:
            st.markdown("#### Sideboard Analysis")
            render_section_analysis(selected_deck, df_inventory, side_df, "side_analysis")

        # --- Render Top Right Analysis & Preview (LATEST in code flow to fix lag) ---
        with top_col_right:
            st.markdown("#### Mainboard Analysis")
            render_section_analysis(selected_deck, df_inventory, main_df, "main_analysis")
            
            st.divider()
            # This will now correctly reflect changes from any table click immediately
            render_card_preview(st.session_state.selected_card_name, df_inventory, full_deck)

# --- HELPER FUNCTIONS ---

def render_list_table(target_df, label, key_suffix, deck_name):
    st.markdown(f"**{label}** ({target_df['Qty'].sum()})")
    
    # Calculate height to fit content exactly
    calc_height = int((len(target_df) * 35) + 40)
    
    event = st.dataframe(
        target_df[['Qty', 'Name', 'Mana']], 
        use_container_width=True, 
        hide_index=True, 
        height=calc_height,
        on_select="rerun", 
        selection_mode="single-row",
        column_config={
            "Qty": st.column_config.NumberColumn(width=42), 
            "Mana": st.column_config.Column(width=42),
            "Name": st.column_config.Column(width="auto")
        },
        key=f"tab_{key_suffix}_{deck_name}"
    )
    
    if event.selection.rows:
        new_selection = target_df.iloc[event.selection.rows[0]]['Name']
        if st.session_state.selected_card_name != new_selection:
            st.session_state.selected_card_name = new_selection
            st.rerun()

def render_section_analysis(deck_name, df_inventory, section_df, key_prefix):
    if section_df.empty:
        return
    
    missing_data = []
    owned_count = 0
    total_needed = section_df['Qty'].sum()

    for _, row in section_df.iterrows():
        name = row['Name']
        needed = row['Qty']
        price = row['Price']
        
        inv_match = df_inventory[df_inventory['Name'] == name]
        owned = inv_match['Qty'].sum()
        owned_count += min(needed, owned)
        
        if owned < needed:
            missing_data.append({
                "Need": needed - owned,
                "Card": name,
                "Price": float(price)
            })

    # UI: Progress and Metrics
    st.progress(owned_count / total_needed if total_needed > 0 else 0)
    m1, m2 = st.columns(2)
    
    total_val = (section_df['Qty'] * section_df['Price']).sum()
    m1.metric("Value", f"${total_val:.2f}")
    
    if missing_data:
        m_df = pd.DataFrame(missing_data)
        buy_total = (m_df['Need'] * m_df['Price']).sum()
        m2.metric("To Buy", f"${buy_total:.2f}")
        
        m_event = st.dataframe(
            m_df, use_container_width=True, hide_index=True,
            on_select="rerun", selection_mode="single-row",
            column_config={
                "Need": st.column_config.NumberColumn(width=42), 
                "Price": st.column_config.NumberColumn(width=42, format="$%.2f"),
                "Card": st.column_config.Column(width="auto")
            },
            key=f"miss_{key_prefix}_{deck_name}"
        )
        if m_event.selection.rows:
            new_m_selection = m_df.iloc[m_event.selection.rows[0]]['Card']
            if st.session_state.selected_card_name != new_m_selection:
                st.session_state.selected_card_name = new_m_selection
                st.rerun()
    else:
        m2.metric("To Buy", "$0.00")
        st.success("Complete!")

def render_card_preview(name, df_inventory, full_deck):
    img_url = CARD_BACK_URL
    price = 0.0
    display_name = "Selection Preview"

    if name:
        display_name = name
        inv_match = df_inventory[df_inventory['Name'] == name]
        deck_match = full_deck[full_deck['Name'] == name]
        
        # Priority: Inventory Image/Price -> Decklist Image/Price
        if not inv_match.empty:
            img_url = inv_match.iloc[0].get('Image URL', CARD_BACK_URL)
            price = inv_match.iloc[0].get('Price', 0.0)
        elif not deck_match.empty:
            img_url = deck_match.iloc[0].get('Image URL', CARD_BACK_URL)
            price = deck_match.iloc[0].get('Price', 0.0)

    st.markdown(f"#### 🔎 {display_name}")
    p1, p2 = st.columns([1, 1.2])
    with p1:
        # Handle cases where URL might be NaN or Empty
        final_img = img_url if pd.notna(img_url) and img_url else CARD_BACK_URL
        st.image(final_img)
    with p2:
        st.metric("Market Price", f"${float(price):.2f}")
        st.caption("Click any row to update preview.")