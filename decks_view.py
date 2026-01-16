import streamlit as st
import pandas as pd

def render_decks_view(df_inventory, df_all_decks):
    if 'deck_selector_key' not in st.session_state:
        st.session_state.deck_selector_key = 0
    if 'selected_card_name' not in st.session_state:
        st.session_state.selected_card_name = None

    col_left, col_right = st.columns([1.5, 1], gap="large")

    with col_left:
        deck_options = ["Select Deck..."] + sorted(df_all_decks['DeckName'].unique().tolist())
        
        selected_deck = st.selectbox(
            "Select a Deck", 
            options=deck_options,
            key=f"deck_select_{st.session_state.deck_selector_key}"
        )

        if selected_deck != "Select Deck...":
            sub_col1, sub_col2 = st.columns([1, 1], gap="medium")
            
            full_main_df = df_all_decks[
                (df_all_decks['DeckName'] == selected_deck) & 
                (df_all_decks['Section'].str.lower() == 'main')
            ].copy()
            
            working_df = full_main_df.copy()

            # Column configurations for sizing
            # Fixed: Use Column for generic text/mana, NumberColumn for Price/Qty
            main_table_conf = {
                "Qty": st.column_config.NumberColumn(width=42),
                "Mana": st.column_config.Column(width=42),
                "Name": st.column_config.Column(width="auto")
            }

            def render_type_table(target_df, type_label):
                st.markdown(f"**{type_label}s** ({target_df['Qty'].sum()})")
                calc_height = (len(target_df) * 35) + 40
                
                event = st.dataframe(
                    target_df[['Qty', 'Name', 'Mana']], 
                    use_container_width=True, 
                    hide_index=True, 
                    height=int(calc_height),
                    on_select="rerun",
                    selection_mode="single-row",
                    column_config=main_table_conf,
                    key=f"table_{type_label}_{selected_deck}" # Unique key per table
                )
                
                if event.selection.rows:
                    selected_idx = event.selection.rows[0]
                    st.session_state.selected_card_name = target_df.iloc[selected_idx]['Name']

            col1_types = ['Creature', 'Instant', 'Sorcery']
            col2_types = ['Artifact', 'Enchantment', 'Land']

            with sub_col1:
                for t in col1_types:
                    type_df = working_df[working_df['Type'].str.contains(t, na=False)]
                    if not type_df.empty:
                        render_type_table(type_df, t)
                        working_df = working_df.drop(type_df.index)
                    else:
                        st.markdown(f"**{t}s** (0)")
                        st.caption("_No cards of this type_")

            with sub_col2:
                for t in col2_types:
                    type_df = working_df[working_df['Type'].str.contains(t, na=False)]
                    if not type_df.empty:
                        render_type_table(type_df, t)
                        working_df = working_df.drop(type_df.index)
                    else:
                        st.markdown(f"**{t}s** (0)")
                        st.caption("_No cards of this type_")

    with col_right:
        if selected_deck != "Select Deck...":
            # 1. Deck Analysis Logic
            missing_df = render_deck_analysis(selected_deck, df_inventory, full_main_df)
            
            if missing_df is not None and not missing_df.empty:
                st.subheader("🛒 Missing Cards")
                # Fixed Column Config for Missing Table
                missing_conf = {
                    "Need": st.column_config.NumberColumn(width=42),
                    "Avg Price": st.column_config.NumberColumn("Price", width=42, format="$%.2f"),
                    "Card": st.column_config.Column(width="auto")
                }

                m_event = st.dataframe(
                    missing_df[['Need', 'Card', 'Avg Price']],
                    use_container_width=True,
                    hide_index=True,
                    on_select="rerun",
                    selection_mode="single-row",
                    column_config=missing_conf,
                    key=f"missing_table_{selected_deck}"
                )
                if m_event.selection.rows:
                    idx = m_event.selection.rows[0]
                    st.session_state.selected_card_name = missing_df.iloc[idx]['Card']

            st.divider()
            
            # 2. Card Preview Logic
            if st.session_state.selected_card_name:
                name = st.session_state.selected_card_name
                st.subheader(f"🔍 {name}")
                
                inv_match = df_inventory[df_inventory['Name'] == name]
                deck_match = full_main_df[full_main_df['Name'] == name]
                
                # Fetch Data
                img_url = inv_match.iloc[0]['Image URL'] if not inv_match.empty else deck_match.iloc[0]['Image URL']
                price = inv_match.iloc[0]['Price'] if not inv_match.empty else 0.0
                
                p_col1, p_col2 = st.columns([1, 1.2])
                with p_col1:
                    st.image(img_url) if img_url else st.warning("No image")
                with p_col2:
                    st.metric("Market Price", f"${price:.2f}")
                    if st.button("Clear Selection", type="primary"):
                        st.session_state.selected_card_name = None
                        st.rerun()
            else:
                st.info("Select a card to view details.")

def render_deck_analysis(deck_name, df_inventory, main_deck):
    st.title(f"{deck_name}")
    total_needed = main_deck['Qty'].sum()
    missing_list = []
    owned_in_deck = 0

    for _, row in main_deck.iterrows():
        name = row['Name']
        needed = row['Qty']
        inv_match = df_inventory[df_inventory['Name'] == name]
        owned = inv_match['Qty'].sum()
        owned_in_deck += min(needed, owned)
        
        if owned < needed:
            avg_p = inv_match['Price'].mean() if not inv_match.empty else 0.0
            missing_list.append({"Card": name, "Need": needed - owned, "Avg Price": avg_p})

    pct = owned_in_deck / total_needed if total_needed > 0 else 0
    st.write(f"**Deck Completion: {owned_in_deck} / {total_needed}**")
    st.progress(pct)
    
    return pd.DataFrame(missing_list) if missing_list else None