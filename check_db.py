import sqlite3
import pandas as pd

DB_PATH = "data/mtg_pauper.db"

def check_raw_data():
    conn = sqlite3.connect(DB_PATH)
    print("--- RAW DB CHECK ---")
    
    # Check what's actually in the table
    df = pd.read_sql("SELECT * FROM battle_box LIMIT 20", conn)
    
    print("Column names found:", df.columns.tolist())
    print("\nFirst 20 rows:")
    print(df)
    
    """ Count empty values properly
    nan_count = df['rarity'].isna().sum()
    empty_str_count = (df['rarity'].astype(str).str.strip() == "").sum()
    
    print(f"\nAnalysis:")
    print(f"- Total rows checked: {len(df)}")
    print(f"- Actual NaNs: {nan_count}")
    print(f"- Empty strings: {empty_str_count}")
    """
    conn.close()

if __name__ == "__main__":
    check_raw_data()