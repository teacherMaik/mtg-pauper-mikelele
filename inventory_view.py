## Inventory View

import streamlit as st
import pandas as pd

def render_inventory_view(df_inventory, df_all_decks, last_update):
    col_left, col_right = st.columns([1.5, 1], gap="large")

    with col_left:
        st.caption(f"*Last update on {last_update}")
        search = st.text_input("Search card name...", key="inv_search")
        display_df = df_inventory
        if search:
            display_df = df_inventory[df_inventory['Name'].str.contains(search, case=False, na=False)]

        st.markdown("### Inventory List")
        
        # Define how columns should look
        # This adds the $ sign and ensures 2 decimal places natively
        column_configuration = {
            "Name": st.column_config.TextColumn("Name", width="medium"),
            "Qty": st.column_config.NumberColumn("Qty", format="%d", width=42),
            "Price": st.column_config.NumberColumn("Price", format="$%.2f", width=63),
            "Total": st.column_config.NumberColumn("Total", format="$%.2f", width=63),
        }

        event = st.dataframe(
            display_df[['Name', 'Code', 'Qty', 'Price', 'Total',]], # Added Price and Total
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            column_config=column_configuration # Applied the $ formatting
        )

        if event.selection.rows:
            selected_idx = event.selection.rows[0]
            card_data = display_df.iloc[selected_idx]
            card_name = card_data['Name']

            table_col, spacer_col = st.columns([2, 1])

            with table_col:
            
                # --- CARD SPECS TABLE ---
                st.markdown("### Card Specs")
                specs_list = [
                    {"Attribute": "Set", "Value": card_data.get('Edition')},
                    {"Attribute": "Rarity", "Value": card_data.get('Rarity')},
                    {"Attribute": "Type", "Value": card_data.get('Type')},
                    {"Attribute": "Mana", "Value": card_data.get('Mana')}
                ]
                st.dataframe(pd.DataFrame(specs_list), use_container_width=True, hide_index=True)

                # --- DECK SPECS CALCULATIONS ---
                st.markdown("### Deck Specs")
                
                # 1. SUM ALL COPIES IN ENTIRE INVENTORY (regardless of set/printing)
                # This finds every row with the same name and adds up their 'Qty'
                total_inventory = df_inventory[df_inventory['Name'] == card_name]['Qty'].sum()

                # 2. Calculate Deck Needs
                matching_decks = df_all_decks[df_all_decks['Name'] == card_name]
                total_needed_for_decks = matching_decks['Qty'].sum() if not matching_decks.empty else 0
                
                # 3. Calculate Missing & Money
                needed_to_buy = max(0, total_needed_for_decks - total_inventory)
                price_each = card_data.get('Price', 0.0)
                money_needed = needed_to_buy * price_each

                # Create the display table
                deck_specs_list = [
                    {"Attribute": "In Collection", "Value": str(total_inventory)},
                    {"Attribute": "Needed for Decks", "Value": str(total_needed_for_decks)},
                    # Adding the "~" prefix here
                    {"Attribute": "Dineros (Missing)", "Value": f"~ ${money_needed:,.2f}"}
                ]

                # 3. Append individual deck names
                if not matching_decks.empty:
                    for _, deck_row in matching_decks.iterrows():
                        deck_specs_list.append({
                            "Attribute": "In Deck", 
                            "Value": f"{deck_row['DeckName']} ({deck_row['Qty']})"
                        })
                else:
                    deck_specs_list.append({"Attribute": "In Deck", "Value": "None"})

                # 4. Display Deck Specs and Caption note
                st.dataframe(pd.DataFrame(deck_specs_list), use_container_width=True, hide_index=True)
                st.caption(f"*'In Collection' counts all printings of {card_name} owned. The {money_needed} is calculated by the Selected Card's price if you were to buy all needed copies of this edition.")

    with col_right:
        # (Image rendering remains the same)
        if event.selection.rows:
            card_data = display_df.iloc[event.selection.rows[0]]
            st.write(f"### {card_data['Name']}")
            st.image(card_data['Image URL'], width=400)
        else:
            st.info("Select a card to view artwork.")
            st.image("https://static.wikia.nocookie.net/mtgsalvation_gamepedia/images/f/f8/Magic_card_back.jpg", width=420)