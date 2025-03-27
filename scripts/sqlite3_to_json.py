import os
import sqlite3
import json
from config.variables import DATA_DIR


def sqlite_to_json(DB_NAME, TABLE_NAME, JSON_FILE=None):
    # Construct full paths
    db_path = os.path.join(DATA_DIR, DB_NAME)
    json_path = os.path.join(DATA_DIR, JSON_FILE) if JSON_FILE else None

    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Fetch all rows from the given table
    cursor.execute(f"SELECT * FROM {TABLE_NAME}")
    rows = cursor.fetchall()

    # Get column names from cursor description
    column_names = [desc[0] for desc in cursor.description]

    # Convert rows into JSON format (list of dictionaries)
    data = [dict(zip(column_names, row)) for row in rows]

    # Convert to JSON string
    json_data = json.dumps(data, indent=4)

    # Write to a JSON file if specified
    if json_path:
        with open(json_path, "w", encoding="utf-8") as f:
            f.write(json_data)

    # Close the database connection
    conn.close()

    return json_data  # Returning JSON string

# Example usage:
# sqlite_to_json("data1.db", "cis_controls", "output.json")
