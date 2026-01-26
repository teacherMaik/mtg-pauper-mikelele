import streamlit as st
import pandas as pd
import features
import plotly.express as px

def render_inventory_stats_view(df_inventory, df_all_decks):
    # 1. Get Collection Stats
    rarity_inventory = features.get_rarity_stats(df_inventory)
    rarity_inventory = rarity_inventory.rename(columns={'Rarity': 'Stat'})

    # 2. REUSE the same function for Decks
    # We rename columns immediately so we can tell them apart in the merge
    rarity_decks = features.get_rarity_stats(df_all_decks)
    rarity_decks = rarity_decks.rename(columns={
        'Rarity': 'Stat',
        'Count': 'In_Decks_Qty',
        'Value': 'In_Decks_Val'
    })

    # 3. Create the Summary Row (Calculating totals for both)
    summary_data = pd.DataFrame([{
        'Stat': 'Total Cards',
        'Count': df_inventory['Qty'].sum(),
        'Value': df_inventory['Total'].sum(),
        'In_Decks_Qty': df_all_decks['Qty'].sum(),
        'In_Decks_Val': df_all_decks['Total'].sum()
    }])

    # 4. Merge and Stack
    # We merge on 'Stat'. Use how='left' to keep all collection rarities
    rarity_combined = pd.merge(rarity_inventory, rarity_decks, on='Stat', how='left').fillna(0)
    
    full_stats_df = pd.concat([summary_data, rarity_combined], ignore_index=True)
    full_stats_df = full_stats_df.sort_values(by='Count', ascending=False).reset_index(drop=True)

    # 5. Styling & Rendering
    def apply_row_gradient(s):
        colors = ['background-color: #2c3e50; color: white;', 'background-color: #34495e; color: white;', 
                  'background-color: #5d6d7e;', 'background-color: #85929e;', 
                  'background-color: #abb2b9;', 'background-color: #ced3d7;', 'background-color: #ebedef;']
        return [colors[s.name] if s.name < len(colors) else ''] * len(s)

    row_1_col_left, row_1_col_right = st.columns([1.3, 0.7], gap="large")

    with row_1_col_left:
        st.markdown("### Collection vs. Decks")
        styled_df = full_stats_df.style.apply(apply_row_gradient, axis=1)

        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Stat": "Category",
                "Count": st.column_config.NumberColumn("Total Qty", format="%d"),
                "Value": st.column_config.NumberColumn("Total Val", format="$%.2f"),
                "In_Decks_Qty": st.column_config.NumberColumn("In Decks", format="%d"),
                "In_Decks_Val": st.column_config.NumberColumn("Deck Val", format="$%.2f"),
            }
        )

    with row_1_col_right:
        st.markdown("### Top Sets by Volume")
        
        # 1. Fetch the data
        set_data = features.get_set_stats(df_inventory)
        
        # Optional: Group smaller sets into "Other" if the list is huge
        top_sets = set_data.head(12) 

        # 2. Build the Pie Chart
        fig = px.pie(
            top_sets, 
            values='Count', 
            names='Edition',
            hole=0.4,
            color_discrete_sequence=px.colors.sequential.Blues_r
        )

        # 3. Enhance Tooltips and Layout
        fig.update_traces(
            textinfo='percent',
            hovertemplate="<b>%{label}</b><br>Cards: %{value}<br>Value: $%{customdata:,.2f}<extra></extra>",
            customdata=top_sets['Value'],
            marker=dict(line=dict(color='#222222', width=1))
        )

        fig.update_layout(
            showlegend=True,
            # Puts legend on the right for sets, as names can be long
            legend=dict(orientation="v", yanchor="middle", y=0.5, xanchor="left", x=1.0),
            margin=dict(l=10, r=10, t=10, b=10),
            height=350
        )

        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
    
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

