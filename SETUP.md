# 🛠️ Setup & Usage Guide

Follow these steps to fork this repository and connect it to your own MTG collection data.

## Data Prerequisites
For the engine to run, you must provide the following files in the `/data` directory:

* **inventory.csv**: Exported from [Deckbox.org](https://deckbox.org). 
Ensure all 'Extra Columns' are selected before download:
* Decks Count
* Type
* Cost
* Rarity
* Price
* Image URL
* Last Updated
* TcgPlayer ID
* Scryfall ID

* **Decks Folder**: Individual `.csv` files for each deck. Ensure all same 'Extra Columns' are present (same as inventory)

* **battle_box.csv**: A CSV export of your prioritization sheet. Replicate Column Names for consistency

⚠️ Ensure all paths, file names and prefixes are adapted in the build_db.py ⚠️

* **Custommize MAPS**: In `maps_decks.py` and `maps_utilities.py` update map information according to your specific collection and decks

## 2. Environment Setup
This project requires Python 3.9+ and Streamlit 1.35+.

```bash
# Clone your fork
git clone [https://github.com/YOUR_USERNAME/mtg-pauper-playground.git](https://github.com/YOUR_USERNAME/mtg-pauper-playground.git)

# Install dependencies
pip install -r requirements.txt

# Build Data Base
python build_db.py

# Run Streamlit
streamlit run app.py

## 3. Deployment to Streamlit Community Cloud

Once you have verified the app works locally, follow these steps to host it online:

### Push to GitHub
Ensure all your modified files, including the generated database, are pushed to your fork. 
> **Note:** Check your `.gitignore` file. Ensure it is **not** blocking `.db` or your `/data` folder, otherwise the live app will be empty.

```bash
git add .
git commit -m "Finalizing data and maps for deployment"
git push origin main

### Connect to Streamlit Cloud
1. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/).
2. Click **"New app"** and then select **"Use existing repo"**.
3. Paste your GitHub repository URL.
4. Set the **Main file path** to `app.py`.
5. Click **"Deploy!"**


### 3. Data Maintenance & Updates

Because this app uses a local SQLite database for speed, you need to follow this "Sync" workflow whenever your collection changes:

1. **Update Sources:** Download your new `inventory.csv` from Deckbox and save it to `/data`.
2. **Rebuild:** Run `python build_db.py` on your computer. This processes the new CSVs and updates `inventory.db`.
3. **Sync to Cloud:** Commit and push the updated files to GitHub:
   ```bash
   git add data/ inventory.db
   git commit -m "Update collection data"
   git push origin main