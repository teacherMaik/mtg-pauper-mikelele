import streamlit as st
import pandas as pd

def render_card_search_view(df_inventory, df_all_decks):
    col_left, col_right = st.columns([1.5, 1], gap="large")

    with col_left:
        search = st.text_input("Search card name...", key="inv_search")
        
        # --- DATA CLEANUP ---
        # Ensure code doesn't show as 211.0
        display_df = df_inventory.copy()
        display_df['code'] = display_df['code'].astype(str).str.replace(r'\.0$', '', regex=True)
        
        if search:
            display_df = display_df[display_df['name'].str.contains(search, case=False, na=False)]

        st.markdown("### Inventory List")
        
        # --- UPDATED COLUMN CONFIGURATION ---
        column_configuration = {
            "name": st.column_config.TextColumn("Name", width="medium"),
            "code": st.column_config.TextColumn("Code", width="small"),
            "qty": st.column_config.NumberColumn("Qty", format="%d", width=42),
            "price": st.column_config.NumberColumn("Price", format="$%.2f", width=75),
            "total_cards_value": st.column_config.NumberColumn("Total Value", format="$%.2f", width=100),
        }

        event = st.dataframe(
            display_df[['name', 'code', 'qty', 'price', 'total_cards_value']],
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            column_config=column_configuration
        )

        if event.selection.rows:
            selected_idx = event.selection.rows[0]
            card_data = display_df.iloc[selected_idx]
            card_name = card_data['name']

            table_col, spacer_col = st.columns([2, 1])

            with table_col:
                # --- CARD SPECS TABLE ---
                st.markdown("### Card Specs")
                specs_list = [
                    {"Attribute": "Set", "Value": card_data.get('edition')},
                    {"Attribute": "Rarity", "Value": card_data.get('rarity')},
                    {"Attribute": "Type", "Value": card_data.get('type')},
                    {"Attribute": "Mana", "Value": card_data.get('mana')},
                    {"Attribute": "Price", "Value": f"${card_data.get('price', 0.0):,.2f}"}
                ]
                # Removing headers by setting labels to empty strings
                st.dataframe(
                    pd.DataFrame(specs_list), 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "Attribute": st.column_config.TextColumn(label=""),
                        "Value": st.column_config.TextColumn(label="")
                    }
                )

                # --- DECK SPECS CALCULATIONS ---
                st.markdown("### Deck Specs")
                
                total_inventory = df_inventory[df_inventory['name'] == card_name]['qty'].sum()
                matching_decks = df_all_decks[df_all_decks['name'] == card_name]
                total_needed_for_decks = matching_decks['qty'].sum() if not matching_decks.empty else 0
                
                needed_to_buy = max(0, total_needed_for_decks - total_inventory)
                price_each = card_data.get('price', 0.0)
                money_needed = needed_to_buy * price_each

                deck_specs_list = [
                    {"Attribute": "In Collection", "Value": str(int(total_inventory))},
                    {"Attribute": "Needed for Decks", "Value": str(int(total_needed_for_decks))},                 
                ]

                if not matching_decks.empty:
                    for _, deck_row in matching_decks.iterrows():
                        deck_specs_list.append({
                            "Attribute": f"{deck_row['DeckName']}", 
                            "Value": int(deck_row['qty'])
                        })

                    deck_specs_list.append({"Attribute": "Cards Missing", "Value": str(needed_to_buy)})
                    deck_specs_list.append({"Attribute": "$ Needed", "Value": f"~ ${money_needed:,.2f}"})
                else:
                    deck_specs_list.append({"Attribute": "In Deck", "Value": "None"})

                # Removing headers by setting labels to empty strings
                st.dataframe(
                    pd.DataFrame(deck_specs_list), 
                    use_container_width=True, 
                    hide_index=True,
                    column_config={
                        "Attribute": st.column_config.TextColumn(label=""),
                        "Value": st.column_config.TextColumn(label="")
                    }
                )
                st.caption(f"*'In Collection' counts all printings of {card_name}. Price used: ${price_each:,.2f}")
    with col_right:
        if event.selection.rows:
            card_data = display_df.iloc[event.selection.rows[0]]
            st.write(f"### {card_data['name']}")
            # Use a container to keep the image size stable
            with st.container():
                st.image(card_data['image_url'], use_container_width=True)
        else:
            st.info("Select a card to view artwork.")
            st.image("https://static.wikia.nocookie.net/mtgsalvation_gamepedia/images/f/f8/Magic_card_back.jpg", width=420)