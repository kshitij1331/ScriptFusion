import os
import pandas as pd
import sqlite3
from config.variables import DATA_DIR


def xlsx_to_sqlite(XLSX_FILE, SUBSHEET_NAME, DB_NAME, TABLE_NAME):
    # Construct full paths
    xlsx_path = os.path.join(DATA_DIR, XLSX_FILE)
    db_path = os.path.join(DATA_DIR, DB_NAME)

    # Read the Excel file
    df = pd.read_excel(xlsx_path, sheet_name=SUBSHEET_NAME, engine="openpyxl")
    
    # Replace spaces in column names with underscores
    df.columns = [col.replace(" ", "_") for col in df.columns]
    
    # Connect to SQLite database (creates file if it doesn't exist)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Automatically create table with column names based on the modified DataFrame
    columns = ", ".join([f'"{col}" TEXT' for col in df.columns])  # All columns as TEXT
    cursor.execute(f'CREATE TABLE IF NOT EXISTS {TABLE_NAME} (id INTEGER PRIMARY KEY AUTOINCREMENT, {columns})')
    
    # Insert data into the table
    df.to_sql(TABLE_NAME, conn, if_exists="append", index=False)
    
    # Commit changes and close connection
    conn.commit()
    conn.close()
    
    print(f"Excel data from sheet '{SUBSHEET_NAME}' successfully stored in '{db_path}' (Table: {TABLE_NAME})")

# Example usage:
# xlsx_to_sqlite("CIS_Red_Hat_Enterprise_Linux_8_Benchmark_v3.0.0.xlsx", "Sheet1", "data1.db", "cis_controls")
