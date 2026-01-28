import streamlit as st
import pandas as pd
import features
import plotly.express as px

METALLIC_GRAY = "#2c3e50"

def render_row_1(df_inventory, df_all_decks):
    # --- Aggregation for Main Table ---
    rarity_inv = features.get_rarity_stats(df_inventory).rename(
        columns={'rarity': 'Stat', 'qty': 'Count', 'total_cards_value': 'Value'}
    )
    rarity_deck = features.get_rarity_stats(df_all_decks).rename(
        columns={'rarity': 'Stat', 'qty': 'In_Decks_Qty', 'total_cards_value': 'In_Decks_Val'}
    )
    rarity_combined = pd.merge(rarity_inv, rarity_deck, on='Stat', how='left').fillna(0)
    rarity_combined['Usage_Pct'] = ((rarity_combined['In_Decks_Qty'] / rarity_combined['Count']) * 100).fillna(0)

    # Main Summary Row
    total_qty, deck_qty = df_inventory['qty'].sum(), df_all_decks['qty'].sum()
    summary_data = pd.DataFrame([{
        'Stat': 'Total Cards',
        'Count': total_qty,
        'Value': df_inventory['total_cards_value'].sum(),
        'Usage_Pct': ((deck_qty / total_qty) * 100) if total_qty > 0 else 0,
        'In_Decks_Qty': deck_qty,
        'In_Decks_Val': df_all_decks['total_cards_value'].sum()
    }])
    
    # Sort the rarity rows by Count before adding the summary row at the top
    rarity_sorted = rarity_combined.sort_values(by='Count', ascending=False)
    full_rarity_df = pd.concat([summary_data, rarity_sorted], ignore_index=True)

    # --- Aggregation for Land Table ---
    land_inv = features.get_land_breakdown(df_inventory)
    land_deck = features.get_land_breakdown(df_all_decks).rename(
        columns={'Count': 'In_Decks_Qty', 'Value': 'In_Decks_Val'}
    )
    
    land_combined = pd.merge(land_inv, land_deck, on='Stat', how='left').fillna(0)
    land_combined['Usage_Pct'] = ((land_combined['In_Decks_Qty'] / land_combined['Count']) * 100).fillna(0)

    # --- Shared Column Configuration ---
    # --- Define a unified width for each column to force alignment ---
    COL_WIDTHS = {
        "Stat": 120,
        "Count": 60,
        "Value": 80,
        "Usage_Pct": 120,
        "In_Decks_Qty": 100,
        "In_Decks_Val": 120
    }

    # --- Shared Configuration for both tables ---
    shared_config = {
        "Stat": st.column_config.TextColumn(" ", width=COL_WIDTHS["Stat"]),
        "Count": st.column_config.NumberColumn("Qty", format="%d", width=COL_WIDTHS["Count"]),
        "Value": st.column_config.NumberColumn("Value", format="$%.2f", width=COL_WIDTHS["Value"]),
        "Usage_Pct": st.column_config.ProgressColumn("% in Decks", format="%.1f%%", min_value=0, max_value=100, width=COL_WIDTHS["Usage_Pct"]),
        "In_Decks_Qty": st.column_config.NumberColumn("Qty in Decks", format="%d", width=COL_WIDTHS["In_Decks_Qty"]),
        "In_Decks_Val": st.column_config.NumberColumn("Value in Decks", format="$%.2f", width=COL_WIDTHS["In_Decks_Val"])
    }

    # UI columns
    c1, c2 = st.columns([1, 1], gap="large")
    with c1:
        st.markdown("## Collection & Decks")
        # Main Table
        st.dataframe(
            full_rarity_df.style.apply(lambda s: [f'background-color: {METALLIC_GRAY}; color: white;' if s.name == 0 else '' for _ in s], axis=1),
            use_container_width=True, hide_index=True,
            column_config=shared_config
        )
        
        # Land Table (Directly beneath, no visible headers)
        st.dataframe(
            land_combined, 
            use_container_width=True, 
            hide_index=True, 
            column_order=("Stat", "Count", "Value", "Usage_Pct", "In_Decks_Qty", "In_Decks_Val"),
            column_config=shared_config
        )
    
    with c2:
        with st.container(border=True):
            st.markdown("### Top 12 Sets")
            metallic_gradient = [
                '#2c3e50', '#34495e', '#415a77', '#516a89', 
                '#617a9b', '#718aad', '#829abf', '#93abd1', 
                '#a4bce3', '#b5cdf5', '#c6def7', '#d7efff'
            ]

            sort_metric = st.radio("Rank Sets:", options=["Qty", "Val"], horizontal=True, label_visibility="collapsed", key="set_sort")
            col_key = 'qty' if sort_metric == "Qty" else 'total_cards_value'
            set_data = features.get_set_stats(df_inventory).sort_values(by=col_key, ascending=False).head(12)
            fig = px.pie(set_data, values=col_key, names='edition', hole=0.4, color_discrete_sequence=metallic_gradient)
            # Custom hover: Bold Name, clean Qty/Value labels

            # Determine formatting based on metric
            if sort_metric == "Qty":
                # Shows: 474
                htemplete = "<b>%{label}</b><br>Qty: %{value}<extra></extra>"
            else:
                # Shows: $123.45 (:.2f adds two decimals)
                htemplete = "<b>%{label}</b><br>Value: $%{value:.2f}<extra></extra>"
                
            fig.update_traces(hovertemplate=htemplete)
            fig.update_layout(showlegend=True, legend=dict(orientation="h", yanchor="bottom", y=-0.7, xanchor="center", x=0.5), height=500, margin=dict(t=0, b=0))
            st.plotly_chart(fig, use_container_width=True)

def render_row_2(df_inventory):
    row_2_col_left, row_2_col_right = st.columns([1, 1], gap="large")

    with row_2_col_left:
        with st.container(border=True):
            st.markdown("### Collection By Color")
            # Filter Pie by Rarity
            all_rarities = df_inventory['rarity'].unique()
            sel_rarity = st.multiselect("Filter Pie by Rarity:", options=all_rarities, key="color_rarity_filter")
            
            df_p = df_inventory[df_inventory['rarity'].isin(sel_rarity)] if sel_rarity else df_inventory
            
            # Message logic for Rarity Filter
            if df_p.empty and sel_rarity:
                st.write("")
                st.info("Mikelele has no such cards...")
                st.write("")
            else:
                color_data, _, _ = features.get_stats(df_p)

                if not color_data.empty:
                    color_map = {
                        'White': '#F0F0F0', 'Blue': '#0000FF', 'Black': '#000000', 
                        'Red': '#FF0000', 'Green': '#008000', 'Colorless': '#90ADBB', 'Land': "#6D5025"
                    }
                    fig_pie = px.pie(color_data, values='Count', names='Color', color='Color', color_discrete_map=color_map, hole=0.4)
                    fig_pie.update_traces(
                        customdata=color_data['Value'], 
                        hovertemplate="<b>%{label}</b><br>Qty: %{value}<br>Value: $%{customdata:,.2f}<extra></extra>", 
                        textinfo='none', 
                        marker=dict(line=dict(color='#444444', width=1.5))
                    )
                    fig_pie.update_layout(showlegend=True, height=350, margin=dict(l=10, r=10, t=10, b=10))
                    st.plotly_chart(fig_pie, use_container_width=True, config={'displayModeBar': False})

    with row_2_col_right:
        with st.container(border=True):
            st.markdown("### Collection By Type")
            # Multiselect options
            sel_color = st.multiselect("Filter by Color:", options=['White', 'Blue', 'Black', 'Red', 'Green', 'Colorless'], key="typ_f")
            
            df_b = df_inventory.copy()
            if sel_color:
                # Map UI names to DB codes
                ui_to_db = {
                    'White': 'W', 'Blue': 'U', 'Black': 'B', 
                    'Red': 'R', 'Green': 'G', 'Colorless': 'C'
                }
                selected_codes = [ui_to_db[c] for c in sel_color if c in ui_to_db]
                
                if selected_codes:
                    # Functional identity: {W}{B} or {WB} matches both White and Black filters
                    pattern = '|'.join(selected_codes)
                    df_b = df_b[df_b['color'].str.contains(pattern, na=False)]
            
            # Message logic for Color Filter
            if df_b.empty and sel_color:
                st.write("")
                st.info("Mikelele has no such cards...")
                st.write("")
            else:
                _, type_data, _ = features.get_stats(df_b)

                if not type_data.empty:
                    # Sort ascending for highest count at top of horizontal chart
                    type_data = type_data.sort_values(by='Count', ascending=True)

                    fig_bar = px.bar(
                        type_data, 
                        x='Count', 
                        y='Type', 
                        orientation='h', 
                        text='Count', 
                        custom_data=['Value'], 
                        color_discrete_sequence=[METALLIC_GRAY]
                    )
                    
                    fig_bar.update_traces(
                        textposition='inside', 
                        textfont=dict(color='white'), 
                        hovertemplate="<b>%{y}</b><br>Qty: %{x}<br>Total Value: $%{customdata[0]:,.2f}<extra></extra>"
                    )
                    
                    fig_bar.update_layout(
                        showlegend=False, 
                        height=350, 
                        margin=dict(l=10, r=10, t=10, b=10), 
                        xaxis_title=None, 
                        yaxis_title=None,
                        yaxis={'categoryorder': 'trace'} # Respect dataframe sort
                    )
                    st.plotly_chart(fig_bar, use_container_width=True)


def render_row_3(df_inventory):
    with st.container(border=True):
        c_head, c_f1, c_f2, c_f3 = st.columns([1, 1.5, 1.5, 0.8])
        with c_head: 
            st.markdown("### Mana Curve")
        with c_f1:
            sel_type = st.multiselect("Filter by Type:", options=['Creature', 'Instant', 'Sorcery', 'Artifact', 'Enchantment'], key="cmc_t_f", label_visibility="collapsed")
        with c_f2:
            sel_color = st.multiselect("Filter by Color:", options=['White', 'Blue', 'Black', 'Red', 'Green', 'Colorless'], key="cmc_c_f", label_visibility="collapsed")
        with c_f3:
            is_transposed = st.toggle("Transpose", key="cmc_transpose")

        # 1. Apply Filtering
        df_c = df_inventory.copy()
        
        if sel_type:
            df_c = df_c[df_c['type'].str.contains('|'.join(sel_type), case=False, na=False)]
            
        if sel_color:
            # Map UI to DB Codes
            ui_to_db = {
                'White': 'W', 'Blue': 'U', 'Black': 'B', 
                'Red': 'R', 'Green': 'G', 'Colorless': 'C'
            }
            selected_codes = [ui_to_db[c] for c in sel_color if c in ui_to_db]
            
            if selected_codes:
                # Regex 'OR' check: a {W}{B} or {WB} card matches if 'White' OR 'Black' is selected
                pattern = '|'.join(selected_codes)
                df_c = df_c[df_c['color'].str.contains(pattern, na=False)]

        # 2. Check for empty results AFTER filtering
        filters_active = any([sel_type, sel_color])

        if df_c.empty and filters_active:
            st.write("") 
            st.info("Mikelele has no such cards...")
            st.write("")
        else:
            # 3. Get Stats and Render Chart
            _, _, cmc_data = features.get_stats(df_c)
            
            if not cmc_data.empty:
                # Ensure CMC is treated as a category for proper discrete axis spacing
                cmc_data = cmc_data.sort_values(by='CMC', ascending=not is_transposed)
                
                if is_transposed:
                    fig_cmc = px.bar(cmc_data, x='Count', y='CMC', orientation='h', text_auto=True, custom_data=['Value'])
                    fig_cmc.update_layout(yaxis=dict(type='category', title="CMC"))
                    # Hover adjustment for horizontal mode
                    h_template = "<b>CMC %{y}</b><br>Qty: %{x}<br>Value: $%{customdata[0]:,.2f}<extra></extra>"
                else:
                    fig_cmc = px.bar(cmc_data, x='CMC', y='Count', text_auto=True, custom_data=['Value'])
                    fig_cmc.update_layout(xaxis=dict(tickmode='linear', dtick=1, title="CMC"))
                    h_template = "<b>CMC %{x}</b><br>Qty: %{y}<br>Value: $%{customdata[0]:,.2f}<extra></extra>"

                fig_cmc.update_traces(
                    marker_color=METALLIC_GRAY, 
                    hovertemplate=h_template
                )
                
                fig_cmc.update_layout(
                    height=400, 
                    margin=dict(l=20, r=20, t=10, b=10), 
                    paper_bgcolor='rgba(0,0,0,0)', 
                    plot_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_cmc, use_container_width=True, config={'displayModeBar': False})


def render_inventory_stats_view(df_inventory, df_all_decks):
    # Pass df_inventory and df_all_decks to your existing render_row_1 logic
    render_row_1(df_inventory, df_all_decks) 
    render_row_2(df_inventory)
    st.divider()
    render_row_3(df_inventory)