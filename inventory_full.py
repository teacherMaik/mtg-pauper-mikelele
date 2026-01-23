import streamlit as st
import pandas as pd

def render_inventory_stats_view(df_inventory, df_all_decks):

    col_left, col_right = st.columns([1.5, 1], gap="large")

    with col_left:
        st.markdown("### Full Inventory List")
        
        # Define how columns should look
        # This adds the $ sign and ensures 2 decimal places natively
        column_configuration = {
            "Name": st.column_config.TextColumn("Name", width="medium"),
            "Qty": st.column_config.NumberColumn("Qty", format="%d", width=42),
            "Price": st.column_config.NumberColumn("Price", format="$%.2f", width=63),
            "Total": st.column_config.NumberColumn("Total", format="$%.2f", width=63),
        }

        event = st.dataframe(
            df_inventory[['Name', 'Code', 'Qty', 'Price', 'Total',]], # Added Price and Total
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            column_config=column_configuration # Applied the $ formatting
        )

        if event.selection.rows:
            selected_idx = event.selection.rows[0]
            card_data = df_inventory.iloc[selected_idx]
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

    with col_right:
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
                'Red': '#FF0000', 'Green': '#008000', 'Colorless': '#90ADBB', 'Land': "#6D5025"
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
                hovertemplate="<b>%{label}</b><br>Qty: %{value}<br>Value: $%{customdata:,.2f}<extra></extra>",
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
                text_auto=True,
                custom_data=['Value'] # Add the new Value column here
            )

            fig_bar.update_traces(
                marker_color="#ED72F1",
                hovertemplate="<b>%{y}</b><br>Cards: %{x}<br>Value: $%{customdata[0]:,.2f}<extra></extra>"
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
    return

