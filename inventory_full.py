import streamlit as st
import pandas as pd
import features
import plotly.express as px

# The metallic gray from your Total Cards row
METALLIC_GRAY = "#2c3e50"

def render_row_1(df_inventory, df_all_decks):
    # --- 1. PROCESS RARITY (Top Table) ---
    rarity_inv = features.get_rarity_stats(df_inventory).rename(columns={'Rarity': 'Stat'})
    rarity_deck = features.get_rarity_stats(df_all_decks).rename(columns={
        'Rarity': 'Stat', 'Count': 'In_Decks_Qty', 'Value': 'In_Decks_Val'
    })
    rarity_combined = pd.merge(rarity_inv, rarity_deck, on='Stat', how='left').fillna(0)
    rarity_combined['Usage_Pct'] = ((rarity_combined['In_Decks_Qty'] / rarity_combined['Count']) * 100).fillna(0)

    # Summary Row
    total_qty, deck_qty = df_inventory['Qty'].sum(), df_all_decks['Qty'].sum()
    summary_data = pd.DataFrame([{
        'Stat': 'Total Cards',
        'Count': total_qty,
        'Value': df_inventory['Total'].sum(),
        'Usage_Pct': ((deck_qty / total_qty) * 100) if total_qty > 0 else 0,
        'In_Decks_Qty': deck_qty,
        'In_Decks_Val': df_all_decks['Total'].sum()
    }])
    full_rarity_df = pd.concat([summary_data, rarity_combined], ignore_index=True)

    # --- 2. PROCESS LANDS (Bottom Table) ---
    land_inv = features.get_land_breakdown(df_inventory)
    land_deck = features.get_land_breakdown(df_all_decks).rename(columns={
        'Count': 'In_Decks_Qty', 'Value': 'In_Decks_Val'
    })
    land_combined = pd.merge(land_inv, land_deck, on='Stat', how='left').fillna(0)
    land_combined['Usage_Pct'] = ((land_combined['In_Decks_Qty'] / land_combined['Count']) * 100).fillna(0)
    
    # Ensure columns match exactly
    cols = ['Stat', 'Count', 'Value', 'Usage_Pct', 'In_Decks_Qty', 'In_Decks_Val']
    full_rarity_df = full_rarity_df[cols].sort_values(by='Count', ascending=False)
    land_combined = land_combined[cols].sort_values(by='Usage_Pct', ascending=False)

    # --- 3. UI RENDERING ---
    def apply_row_gradient(s):
        return ['background-color: #2c3e50; color: white;' if s.name == 0 else '' for _ in s]

    row_1_col_left, row_1_col_right = st.columns([1, 1], gap="large")

    with row_1_col_left:
        st.markdown("## Collection & Decks")
        # Rarity Table
        st.dataframe(
            full_rarity_df.style.apply(apply_row_gradient, axis=1),
            use_container_width=True, hide_index=True,
            column_config={
                "Stat": "Category",
                "Count": st.column_config.NumberColumn("Qty", format="%d"),
                "Value": st.column_config.NumberColumn("Val", format="$%.2f"),
                "Usage_Pct": st.column_config.ProgressColumn("% Usage", format="%.1f%%", min_value=0, max_value=100),
                "In_Decks_Qty": st.column_config.NumberColumn("Decks", format="%d"),
                "In_Decks_Val": st.column_config.NumberColumn("Deck Val", format="$%.2f"),
            }
        )
        
        # Land Table (Headers hidden by empty strings, but columns logic is identical)
        st.dataframe(
            land_combined, 
            use_container_width=True, hide_index=True, 
            column_config={
                "Stat": "", 
                "Count": st.column_config.NumberColumn("", format="%d"),
                "Value": st.column_config.NumberColumn("", format="$%.2f"),
                "Usage_Pct": st.column_config.ProgressColumn("", format="%.1f%%", min_value=0, max_value=100),
                "In_Decks_Qty": st.column_config.NumberColumn("", format="%d"),
                "In_Decks_Val": st.column_config.NumberColumn("", format="$%.2f"),
            }
        )

    with row_1_col_right:
        # ... (Set Pie Chart code remains exactly the same)
        with st.container(border=True):
            # set_intro_col_1, set_intro_col_2 = st.columns([1, 1])
            # with set_intro_col_1: st.markdown("### Top 12 Sets")
            # with set_intro_col_2:
            #     sort_metric = st.radio("Rank Sets:", options=["Count", "Value"], horizontal=True, label_visibility="collapsed", key="set_sort")

            st.markdown("### Top 12 Sets")
            sort_metric = st.radio("Rank Sets:", options=["Count", "Value"], horizontal=True, label_visibility="collapsed", key="set_sort")

            set_data = features.get_set_stats(df_inventory)
            top_sets = set_data.sort_values(by=sort_metric, ascending=False).head(12).copy()
            fig = px.pie(top_sets, values=sort_metric, names='Edition', hole=0.4, color_discrete_sequence=px.colors.sequential.Blues_r)
            
            c_data = top_sets['Value'] if sort_metric == "Count" else top_sets['Count']
            h_temp = "<b>%{label}</b><br>Count: %{value}<br>Value: $%{customdata:,.2f}<extra></extra>" if sort_metric == "Count" else "<b>%{label}</b><br>Value: $%{value:,.2f}<br>Count: %{customdata}<extra></extra>"
            
            fig.update_traces(customdata=c_data, hovertemplate=h_temp, textinfo='percent', marker=dict(line=dict(color='#444444', width=1.5)))
            # Inside render_row_1, Top 12 Sets block
            fig.update_layout(
                showlegend=True,
                legend=dict(
                    orientation="h",   # Horizontal legend
                    yanchor="bottom",
                    y=-0.7,            # Move it below the chart
                    xanchor="center",
                    x=0.5
                ),
                height=560,            # Increase height to account for bottom legend
                margin=dict(l=10, r=10, t=0, b=10),
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})


def render_row_2(df_inventory, df_all_decks):
    row_2_col_left, row_2_col_right = st.columns([1, 1], gap="large")

    with row_2_col_left:
        with st.container(border=True):
            st.markdown("### Collection By Color")
            # Filter for Color Chart
            all_rarities = df_inventory['Rarity'].unique()
            sel_rarity = st.multiselect("Filter Pie by Rarity:", options=all_rarities, placeholder="All Rarities", key="color_rarity_filter")
            
            df_pie = df_inventory[df_inventory['Rarity'].isin(sel_rarity)] if sel_rarity else df_inventory
            color_data, _, _ = features.get_stats(df_pie)

            if not color_data.empty:
                color_map = {'White': '#F0F0F0', 'Blue': '#0000FF', 'Black': '#000000', 'Red': '#FF0000', 'Green': '#008000', 'Colorless': '#90ADBB', 'Land': "#6D5025"}
                fig_pie = px.pie(color_data, values='Count', names='Color', color='Color', color_discrete_map=color_map, hole=0.4)
                fig_pie.update_traces(customdata=color_data['Value'], hovertemplate="<b>%{label}</b><br>Qty: %{value}<br>Value: $%{customdata:,.2f}<extra></extra>", textinfo='none', marker=dict(line=dict(color='#444444', width=1.5)))
                fig_pie.update_layout(showlegend=True, height=300, margin=dict(l=10, r=10, t=10, b=10))
                st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

    with row_2_col_right:
        with st.container(border=True):
            st.markdown("### Collection By Type")
            sel_color = st.multiselect("Filter by Color:", options=['White', 'Blue', 'Black', 'Red', 'Green', 'Colorless'], key="typ_f")
            
            df_bar = df_inventory.copy()
            if sel_color:
                color_map = {'White':'W', 'Blue':'U', 'Black':'B', 'Red':'R', 'Green':'G'}
                codes = [color_map[c] for c in sel_color if c in color_map]
                
                if "Colorless" in sel_color:
                    # Regex for "Does not contain W, U, B, R, or G"
                    mask = ~df_bar['Mana'].str.contains(r'[WUBRG]', case=False, na=True)
                    if codes:
                        # If user selected Colorless AND Blue, show both
                        mask |= df_bar['Mana'].str.contains('|'.join(codes), case=False, na=False)
                    df_bar = df_bar[mask]
                else:
                    df_bar = df_bar[df_bar['Mana'].str.contains('|'.join(codes), case=False, na=False)]
            
            _, type_data, _ = features.get_stats(df_bar)

            if not type_data.empty:
                # 2. Create the horizontal bar chart
                # We pass 'Value' into custom_data so it's available for the hovertemplate
                fig_bar = px.bar(
                    type_data, 
                    x='Count', 
                    y='Type', 
                    orientation='h', 
                    text='Count', # This puts the number on the bar
                    custom_data=['Value'] 
                )

                # 3. Style the bars and the text
                fig_bar.update_traces(
                    marker_color='#FF4B4B',           # Streamlit Primary Red
                    textposition='inside',            # Force text inside the bar
                    textfont=dict(color='white'),     # MAKE TAG WHITE
                    # Fix the hover: customdata[0] refers to 'Value'
                    hovertemplate="<b>%{y}</b><br>Qty: %{x}<br>Total Value: $%{customdata[0]:,.2f}<extra></extra>"
                )

                # 4. Clean up the layout
                fig_bar.update_layout(
                    showlegend=False,
                    height=350,
                    margin=dict(l=10, r=10, t=10, b=10),
                    xaxis_title=None,
                    yaxis_title=None,
                    paper_bgcolor='rgba(0,0,0,0)',
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("No cards found for these filters.")

def render_row_3(df_inventory, df_all_decks):
    with st.container(border=True):
        # Header Row: Title | Type Filter | Color Filter | Transpose Toggle
        # Adjusted columns to fit the new toggle
        c_head, c_f1, c_f2, c_f3 = st.columns([1, 1.5, 1.5, 0.8])
        
        with c_head: 
            st.markdown("### Mana Curve")
            
        with c_f1:
            sel_type = st.multiselect("Filter by Type:", 
                                     options=['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment', 'Planeswalker'], 
                                     placeholder="All Types", key="cmc_type_filter", label_visibility="collapsed")
            
        with c_f2:
            sel_color = st.multiselect("Filter by Color:", 
                                      options=['White', 'Blue', 'Black', 'Red', 'Green', 'Colorless'], 
                                      placeholder="All Colors", key="cmc_color_filter", label_visibility="collapsed")
        
        with c_f3:
            # The "Mobile Transpose" Toggle
            is_transposed = st.toggle("Transpose", key="cmc_transpose")

        # --- Filter Logic (Same as before) ---
        df_cmc_filtered = df_inventory.copy()
        if sel_type:
            df_cmc_filtered = df_cmc_filtered[df_cmc_filtered['Type'].str.contains('|'.join(sel_type), case=False, na=False)]
        if sel_color:
            color_map = {'White':'W', 'Blue':'U', 'Black':'B', 'Red':'R', 'Green':'G'}
            selected_codes = [color_map[c] for c in sel_color if c in color_map]
            if "Colorless" in sel_color:
                mask = (df_cmc_filtered['Mana'].isna()) | (df_cmc_filtered['Mana'] == "")
                if selected_codes: mask |= df_cmc_filtered['Mana'].str.contains('|'.join(selected_codes), case=False, na=False)
                df_cmc_filtered = df_cmc_filtered[mask]
            else:
                df_cmc_filtered = df_cmc_filtered[df_cmc_filtered['Mana'].str.contains('|'.join(selected_codes), case=False, na=False)]

        _, _, cmc_data = features.get_stats(df_cmc_filtered)
        
        if not cmc_data.empty:
            cmc_data = cmc_data.sort_values(by='CMC', ascending=not is_transposed)
            
            # --- Dynamic Orientation ---
            if is_transposed:
                # Horizontal Bar (Best for Mobile)
                fig_cmc = px.bar(cmc_data, x='Count', y='CMC', orientation='h', 
                                 text_auto=True, custom_data=['Value'])
                # Force Y-axis to show every CMC number
                fig_cmc.update_layout(yaxis=dict(type='category', dtick=1, title="Mana Value (CMC)"),
                                      xaxis_title="Total Cards")
            else:
                # Vertical Bar (Standard Desktop)
                fig_cmc = px.bar(cmc_data, x='CMC', y='Count', 
                                 text_auto=True, custom_data=['Value'])
                fig_cmc.update_layout(xaxis=dict(tickmode='linear', dtick=1, title="Mana Value (CMC)"),
                                      yaxis_title="Total Cards")

            fig_cmc.update_traces(
                marker_color=METALLIC_GRAY, 
                hovertemplate="<b>CMC %{x}</b><br>Qty: %{y}<br>Value: $%{customdata[0]:,.2f}<extra></extra>"
            )
            
            fig_cmc.update_layout(
                height=500 if is_transposed else 350, # More height for vertical list of CMC
                margin=dict(l=20, r=20, t=10, b=10),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig_cmc, use_container_width=True, config={'displayModeBar': False})

def render_inventory_stats_view(df_inventory, df_all_decks):
    render_row_1(df_inventory, df_all_decks)
    render_row_2(df_inventory, df_all_decks)
    st.divider()
    render_row_3(df_inventory, df_all_decks)