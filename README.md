# MTG Pauper Playground (2026)
**Live Dashboard:** [pauper-playground.streamlit.app](https://pauper-playground.streamlit.app/)

An advanced, Streamlit-powered analytical dashboard for Magic: The Gathering. This tool provides deep insights into a personal collection and a specialized Pauper Battle Box ecosystem.

---

## Project Areas

* **Battle Box:** A curated environment designed for "grab-and-play" deck pairings. The system tracks card requirements based on **personal deck priorities**, ensuring I own enough physical copies to keep all decks built simultaneously without card-swapping.
* **Collection:** A high-level view of my entire MTG inventory. It tracks total cards, unique counts, and the percentage of the collection currently "active" in decks. It highlights rarity shifts, such as rare/uncommon cards downgraded to Pauper legality.
* **Land Fan:** A dedicated view for land enthusiasts such s myself. Features include a specialized explorer for lands with properties like "Cycling," "Surveil," or "Scry."

---

## Features

### Data Intelligence & Metrics
* **Inventory Overview:** High-level tracking of **Unique Card Counts**, **Total Card Quantities**, and real-time **Card Values** (Price) from enriched data.
* **Deck Integration:** Maps decklists to physical inventory, calculating exactly how many copies are "In Decks".

### Multi-Dimensional Analysis
* **By Colors:** Dynamic WUBRG distribution charts. Instantly switch between **Inventory** (total potential) and **Decks** (actual usage) via radio filters.
* **By Type:** Analysis of card types (Creatures, Instants, Sorceries, etc.) across the collection or specific archetypes.
* **Mana Curve:** Visual representation of Mana Value (CMC) distribution to ensure deck health and Battle Box balance.
* **Staples Heatmap:** A "Top 12" view of the most played cards from decks in my Battle Box. Includes **Archetype Intelligence** to see which cards are critical to Aggro, Control, or Midrange strategies.
* **Sets Analysis:** A breakdown of collection density by set, featuring a gradient-styled view of the top 12 sets in the inventory.

### Dynamic Filtering System
The dashboard utilizes a sophisticated filtering engine that adapts based on the active chart:
* **Conditions:** Filters by **Section** (Main/Sideboard), **Archetype**, and **Rarity**.
* **Smart Search:** A "Global Explorer" that supports **Boolean Tagging**. Search for `artifact`, `gate`, or `fetch` to instantly query pre-engineered boolean columns.
* **Interactive Context:** Selecting a card in a table updates the UI to show card art and a **Deck Usage Table**, comparing **Required** copies vs. **Allocated** copies (`num_for_deck`).

---

## Data Structure
```text
.
├── data/
│   ├── inventory.csv       # CSV exports from deckbox.org
│   ├── battle_box.csv      # CSV from Google Sheets (Deck Priorities)
│   └── decks/              # Individual .csv files for specific decklists
├── build_db.py             # DB ingestion and manual enrichment pipeline to sqlite
├── data_manager.py         # Global state management; caches the 3 main DataFrames
├── app.py                  # Main Streamlit entry and navigation
└── features.py             # Plotly widgets and specialized aggregation logic
```
---

## Data Enrichment Pipeline & Engineering
* **Deck Mapping** (`DECKS_MAP`): Ensures deck cards are correctly matched to the specific set versions in my inventory.
* **Land Mapping** (`LAND_DATA_MAP`): Manual tags are exploded into `is_[tag]` boolean columns for high-speed filtering.
* **String Cleanup:** Mana production strings like `{W}{B}` are cleaned to `WB` to support vectorized searches.

## Optimization & Caching
* **@st.cache_data:** Used for the heavy lifting of filtering and aggregating the Inventory and Deck dataframes.
* **Vectorized Pandas:** All pip-counting and multi-color logic is handled via vectorized operations rather than Python loops for near-instant UI updates.

---

## Configuration
* **Theme:** Dark metallic gray styling for all non-color charts.
* **Color Logic:** `{W}{B}` and `{WB}` are treated as identical for filtering purposes.
* **Image Source:** Uses the `image_url` column directly from the enriched database.

---

*Generated for Masters in Data Science & AI @EBIS Business School*