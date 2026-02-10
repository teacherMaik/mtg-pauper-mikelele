# MTG Pauper Playground

An advanced, Streamlit-powered analytical dashboard for Magic: The Gathering collections. This tool provides deep insights into my personal collection and Decks.

---

## Data Structure
```text
.
├── data/
│   └── inventory (full innventory csv file downloaded from deckbox.org)
│   └── battle_box (csv downloaded from personal Google Sheets for prioritizing decks)
│   └── decks/
│       └── deck_name (csv file for specific decks)
│       └── ...
├── build_db.py (DB ingestion, Manual run)
├── data_manager.py (Caches 3 main DF from db)
├── app.py (Main Streamlit entry and navigation)
```

---

## Areas

### 1. Battle Box
I am buildng a Pauper Battle Box, to be able to grab any 2 decks and play. My goal is to have enough copies of needed cards to not have to switch between decks. I track how many of each cards I need for the decks according to a personal priority of the decks.

### 2. Collection
Inspect my entire MTG collection, viewing Total cards, % of cards in decks, etc. Great to see how many rare or unncommmon cards have been downgraded to Pauper

### 3. Land Fan
Lands are my favorite cards to collect. You can inspect my full land collection, lands in decks, and search by features such as "Cycling, Surveil, Scry, etc..."

---

## Main Features
* **Cards by Color:** Instantly switch between **Inventory** (total potential) and **Decks** (actual usage) via radio filters.
* **Pip-Level Analysis:** Unlike standard tools, this counts actual production pips (e.g., *Vault of Whispers* contributes to Black, *Tundra* contributes to White and Blue).
* **Saturation Visualization:** Uses a custom Plotly widget to show how much of your total land base provides access to specific colors, using a dark metallic gray remainder bar.

### 2. Global Land Explorer (Row 3)
* **Boolean Tag Search:** Power-user search bar. Typing `surveil`, `fetch`, `cycler`, or `artifact` triggers background boolean columns (`is_artifact`, etc.).
* **Interactive Selection:** Selection mode is set to `single-row` with `on_select="rerun"`. Clicking a land instantly updates the card art and usage stats.
* **Allocation Tracking:** A specialized usage table appears under the explorer showing:
    * **Required:** Total copies needed by the decklist.
    * **Allocated:** Actual copies assigned to that deck (`num_for_deck`).
    * **Global Inv:** Total copies owned across all sets in your inventory.

### 3. Top 12 Land Staples
* **Archetype Intelligence:** Filterable heatmap showing which non-basic lands are most critical to specific archetypes (Aggro, Control, etc.).
* **Automatic Filtering:** Automatically excludes basic lands to focus strictly on utility and fixing "staples."

---

## Technical Architecture

### Data Enrichment Pipeline
The system runs a normalization process during the DB build:
* **Key Normalization:** `LAND_DATA_MAP` keys are programmatically lowercased to ensure perfect matches with `MatchName` (e.g., "Vault of Whispers" matches "vault of whispers").
* **Boolean Mapping:** Manual tags are exploded into `is_[tag]` boolean columns for high-speed filtering.
* **String Cleanup:** Mana production strings like `{W}{B}` are cleaned to `WB` to support `.str.contains()` logic in the saturation widgets.

### Optimization & Caching
* **@st.cache_data:** Used for the heavy lifting of filtering and aggregating the Inventory and Deck dataframes.
* **Vectorized Pandas:** All pip-counting and multi-color logic is handled via vectorized operations rather than Python loops for near-instant UI updates.

---


---

## Configuration
* **Theme:** Dark metallic gray styling for all non-color charts.
* **Color Logic:** `{W}{B}` and `{WB}` are treated as identical for filtering purposes.
* **Image Source:** Uses the `image_url` column directly from the enriched database.

---
*Generated for the 2026 MTG Collab.*