import streamlit as st
import pandas as pd

METALLIC_GRAY = "#2c3e50"

def render_wish_list_view(df_all_decks):
    col_left, col_right = st.columns([1.5, 1], gap="large")

    with col_left:
        st.markdown("### My Needs")

        # --- HEADER FILTERS ---
        # Search and Section filter on one line to save vertical space
        f_col1, f_col2 = st.columns([2, 1])
        with f_col1:
            search = st.text_input("Search name...", key="wl_search", label_visibility="collapsed")
        with f_col2:
            # Radio filter for Main/Side/Both
            sec_choice = st.radio("Section", ["Both", "Main", "Side"], horizontal=True, key="wl_sec", label_visibility="collapsed")

        # --- DATA FILTERING ---
        # We start with only cards we need to buy
        display_df = df_all_decks[df_all_decks['need_buy'] > 0].copy()

        if search:
            display_df = display_df[display_df['name'].str.contains(search, case=False, na=False)]
        
        if sec_choice != "Both":
            val = "main" if sec_choice == "Main" else "sideboard"
            display_df = display_df[display_df['section'].str.lower() == val]

        display_df = display_df.sort_values(by=['section', 'Priority'], ascending=[True, True])
        
        # Calculate total for the main table
        display_df['total_need_buy'] = display_df['need_buy'] * display_df['price']

        # --- MAIN NEEDS TABLE ---
        column_configuration = {
            "name": st.column_config.TextColumn("Name", width="medium"),
            "section": st.column_config.TextColumn("Section", width="small"),
            "need_buy": st.column_config.NumberColumn("Qty", format="%d", width=42),
            "price": st.column_config.NumberColumn("Price", format="$%.2f", width=75),
            "total_need_buy": st.column_config.NumberColumn("Total", format="$%.2f", width=100),
        }

        event = st.dataframe(
            display_df[['name', 'section', 'need_buy', 'price', 'total_need_buy', 'DeckName']],
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            column_config=column_configuration,
            key="wl_main_table"
        )

        # --- SELECTION DETAILS ---
        if event.selection.rows:
            selected_idx = event.selection.rows[0]
            card_data = display_df.iloc[selected_idx]
            card_name = card_data['name']
            price_each = card_data['price']

            # --- CARD SPECS TABLE (The Return) ---
            st.markdown("#### Card Details")
            
            # Simple list for the basic attributes
            specs_list = [
                {"Attribute": "Edition", "Value": card_data.get('edition', 'N/A')},
                {"Attribute": "Rarity", "Value": card_data.get('rarity', 'N/A')},
                {"Attribute": "Type", "Value": card_data.get('type', 'N/A')},
                {"Attribute": "Mana", "Value": card_data.get('mana', 'N/A')},
                {"Attribute": "Market Price", "Value": f"${price_each:,.2f}"}
            ]

            st.dataframe(
                pd.DataFrame(specs_list), 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Attribute": st.column_config.TextColumn(label="", width="small"),
                    "Value": st.column_config.TextColumn(label="", width="large")
                }
            )

            # --- DECK SPECS TABLE ---
            st.markdown("#### Requirement per Deck")
            
            matching_decks = df_all_decks[df_all_decks['name'] == card_name]
            
            specs_rows = [{
                "Source": "TOTAL NEEDED",
                "Total": int(matching_decks['qty'].sum()),
                "Own": int(matching_decks['num_for_deck'].sum()),
                "Buy": int(matching_decks['need_buy'].sum()),
                "Money": matching_decks['need_buy'].sum() * price_each
            }]

            for _, row in matching_decks.iterrows():
                specs_rows.append({
                    "Source": row['DeckName'],
                    "Total": int(row['qty']),
                    "Own": int(row['num_for_deck']),
                    "Buy": int(row['need_buy']),
                    "Money": row['need_buy'] * price_each
                })

            df_specs = pd.DataFrame(specs_rows)

            def style_specs_table(row):
                if row.name == 0:
                    return [f'background-color: {METALLIC_GRAY}; color: white; font-weight: bold;'] * len(row)
                styles = [''] * len(row)
                if row['Buy'] > 0:
                    styles[3] = 'color: #ff4b4b; font-weight: bold;'
                return styles

            st.dataframe(
                df_specs.style.apply(style_specs_table, axis=1).format({"Money": "$ {:.2f}"}),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Source": st.column_config.TextColumn("Deck Source", width="medium"),
                    "Total": st.column_config.NumberColumn("Req", width="small"),
                    "Own": st.column_config.NumberColumn("Own", width="small"),
                    "Buy": st.column_config.NumberColumn("Buy", width="small"),
                    "Money": st.column_config.NumberColumn("Value", width="small"),
                }
            )
            st.caption(f"* Own: counts all printings in collection. Unit Price: ${price_each:,.2f}")

    # --- RIGHT COLUMN: ARTWORK ---
    with col_right:
        if event.selection.rows:
            # We already have card_data from the selection logic above
            st.write(f"### {card_data['name']}")
            st.image(card_data.get('image_url', "https://placehold.co/488x680?text=Card+Art"), use_container_width=True)
            
            # Quick stat box under image
            st.metric("Total Investment Needed", f"${df_specs.iloc[0]['Money']:,.2f}")
        else:
            st.info("Select a card to view artwork.")
            st.image("https://static.wikia.nocookie.net/mtgsalvation_gamepedia/images/f/f8/Magic_card_back.jpg", use_container_width=True)


            