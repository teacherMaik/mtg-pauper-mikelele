import streamlit as st
import pandas as pd

def render_deck_detail(deck_name, df_inventory, df_all_decks, df_battle_box):

    deck_cards = df_all_decks[df_all_decks['DeckName'] == deck_name].copy()
    
    # --- ROW 1: HEADER & NAVIGATION ---
    deck_value = deck_cards['total_cards_value'].sum()
    st.markdown(f"""
        <div style="line-height: 1.1;">
            <h2 style="margin: 0; padding: 3px; font-size: 2.2rem;">{deck_name}</h2>
            <div style="font-size: 26px; font-weight: 700; color: #34495e; margin-top: padding: 3px;">
                ~ ${deck_value:,.2f}
            </div>
        </div>
    """, unsafe_allow_html=True)

    deck_view_mode = st.radio(
        "Select View:",
        ["Deck", "Analysis", "Test"],
        horizontal=True,
        label_visibility="collapsed"
    )

    st.divider()

    # --- VIEW ROUTING ---
    if deck_view_mode == "Deck":
        render_deck_list_view(deck_cards)
    elif deck_view_mode == "Analysis":
        st.info("Analysis View - Coming next")
    elif deck_view_mode == "Test":
        st.info("Test View - Coming next")

def render_deck_list_view(deck_cards):

    # 2. Status Logic (using your exact col names)
    deck_cards['status'] = deck_cards.apply(
        lambda x: "✅" if x['num_for_deck'] >= x['qty'] else f"({int(x['num_for_deck'])}/{int(x['qty'])})", 
        axis=1
    )

    # Separate Main vs Side
    mainboard = deck_cards[deck_cards['section'].str.contains('Main', case=False, na=False)]
    sideboard = deck_cards[deck_cards['section'].str.contains('Side', case=False, na=False)]
    
    cards_main = mainboard['qty'].sum()
    cards_main_collected = mainboard['num_for_deck'].sum()
    main_pct = (cards_main_collected / cards_main * 100) if cards_main > 0 else 0
    value_main = mainboard['total_cards_value'].sum()

    cards_side = sideboard['qty'].sum()
    cards_side_collected = sideboard['num_for_deck'].sum()
    side_pct = (cards_side_collected / cards_side * 100) if cards_side > 0 else 0
    value_side = sideboard['total_cards_value'].sum()

    if deck_cards.empty:
        st.error("Deck data not found.")
        return
    
    st.markdown(f"""
        <div style="margin-top:-15px; margin-bottom:15px;">
            <div style="font-size:26px; font-weight:500; margin-bottom:5px;">
                Main ({int(cards_main)}) ~ ${value_main:,.2f}
            </div>
            <div style="background-color: #e0e0e0; border-radius: 5px; width: 210px; height: 8px;">
                <div style="background-color: #34495e; width: {main_pct}%; height: 8px; border-radius: 5px;"></div>
            </div>
            <div style="font-size: 12px; color: #666; margin-top: 2px;">
                {int(cards_main_collected)} / {int(cards_main)} cards collected ({main_pct:.1f}%)
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 4. Mainboard Layout (Wrapped by Type)
    col_left, col_right = st.columns(2, gap="large")
    
    left_types = ['Creature', 'Instant', 'Sorcery']
    right_types = ['Enchantment', 'Artifact', 'Land']

    def draw_type_groups(df, types, ui_col):
        
        with ui_col:
            for t in types:
                # SPECIAL LOGIC: If checking Artifacts, exclude Lands
                if t == 'Artifact':
                    subset = df[
                        (df['type'].str.contains('Artifact', case=False, na=False)) & 
                        (~df['type'].str.contains('Land', case=False, na=False))
                    ]
                else:
                    subset = df[df['type'].str.contains(t, case=False, na=False)]
                
                if not subset.empty:
                    
                    st.markdown(f"#### {t}s ({int(subset['qty'].sum())})")
                    st.dataframe(
                        subset[['qty', 'name', 'mana', 'total_cards_value', 'status']].sort_values("name"),
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "status": st.column_config.TextColumn("Collected", width=65),
                            "qty": st.column_config.NumberColumn("Qty", format="%d", width=35),
                            "name": st.column_config.TextColumn("Name"),
                            "mana": st.column_config.TextColumn("Mana", width=80),
                            "total_cards_value": st.column_config.NumberColumn("Value", format="$ %.2f", width=60)
                        }
                    )
                else:
                    st.markdown(f"""
                        <div style="padding: 15px; border-left: 5px solid #ff4b4b;; background-color: #f8f9fa; color: #34495e; border-radius: 4px; margin-bottom: 20px;">
                            No {t}s in this deck.
                        </div>
                    """, unsafe_allow_html=True)

    draw_type_groups(mainboard, left_types, col_left)
    draw_type_groups(mainboard, right_types, col_right)

    st.divider()

    # 5. Sideboard (Full width below)
    if not sideboard.empty:

        side_col_left, side_col_right = st.columns(2, gap="large")
        

        with side_col_left:
            st.markdown(f"""
                <div style="margin-top:-15px; margin-bottom:15px;">
                    <div style="font-size:26px; font-weight:500; margin-bottom:5px;">
                        Side ({int(cards_side)}) ~ ${value_side:,.2f}
                    </div>
                    <div style="background-color: #e0e0e0; border-radius: 5px; width: 210px; height: 8px;">
                        <div style="background-color: #34495e; width: {side_pct}%; height: 8px; border-radius: 5px;"></div>
                    </div>
                    <div style="font-size: 12px; color: #666; margin-top: 2px;">
                        {int(cards_side_collected)} / {int(cards_side)} cards collected ({side_pct:.1f}%)
                    </div>
                </div>
                """, unsafe_allow_html=True)
            st.dataframe(
                sideboard[['status', 'qty', 'name', 'type', 'mana']].sort_values("name"),
                use_container_width=True,
                hide_index=True,
                column_config={
                    "status": st.column_config.TextColumn("", width=45),
                    "qty": st.column_config.NumberColumn("Qty", format="%d", width=35),
                    "name": st.column_config.TextColumn("Name"),
                    "type": st.column_config.TextColumn("Type"),
                    "mana": st.column_config.TextColumn("Cost", width=60)
                }
            )

        with side_col_right:
            pass