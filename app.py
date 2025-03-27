from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json
import sqlite3
import os
from config.variables import DB_NAME, TABLE_NAME, JSON_FILE, DATA_DIR

app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(DATA_DIR, DB_NAME)
JSON_PATH = os.path.join(DATA_DIR, JSON_FILE)

# ------------------ Utility Functions ------------------

def read_json():
    """Reads JSON data from file."""
    with open(JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def write_json(data):
    """Writes updated JSON data to file."""
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def get_next_db_id():
    """Fetches the next available ID from the SQLite database to keep IDs in sync."""
    with sqlite3.connect(DB_PATH) as con:
        cursor = con.cursor()
        cursor.execute(f"SELECT MAX(id) FROM {TABLE_NAME}")
        max_id = cursor.fetchone()[0]
        return (max_id or 0) + 1  # Ensures ID starts from 1 if the table is empty

def fetch_columns():
    """Fetches column names dynamically from the table, excluding 'id'."""
    with sqlite3.connect(DB_PATH) as con:
        cursor = con.cursor()
        cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
        return [col[1] for col in cursor.fetchall() if col[1] != "id"]

def execute_query(query, values=None, fetch_last_id=False):
    """Executes a SQL query with optional values. Returns last inserted row ID if needed."""
    with sqlite3.connect(DB_PATH) as con:
        cursor = con.cursor()
        cursor.execute(query, values or [])
        con.commit()
        return cursor.lastrowid if fetch_last_id else None

# Load JSON Data
controls = read_json()

# ------------------ Routes ------------------

# Serve the HTML Page
@app.route('/')
def home():
    return render_template("index.html")

# GET all controls
@app.route('/controls', methods=['GET'])
def get_controls():
    return jsonify(controls)

# GET control by ID
@app.route('/controls/<int:control_id>', methods=['GET'])
def get_control(control_id):
    """Fetches a single control by ID from the database to ensure real-time accuracy."""
    with sqlite3.connect(DB_PATH) as con:
        cursor = con.cursor()
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = ?", (control_id,))
        row = cursor.fetchone()

    if row:
        # Convert row to dictionary (assuming column names match JSON structure)
        columns = ["id"] + fetch_columns()  # Ensure "id" is included
        control = dict(zip(columns, row))
        return jsonify(control)
    else:
        return jsonify({"message": "Control not found"}), 404
    

# POST - Add control
@app.route('/controls', methods=['POST'])
def add_control():
    global controls

    data = request.json
    new_id = get_next_db_id()  # Ensure database ID and JSON ID stay in sync
    new_control = {"id": new_id, **data}
    controls.append(new_control)

    # Insert into SQLite
    columns = fetch_columns()
    placeholders = ", ".join(["?" for _ in columns])
    query = f"INSERT INTO {TABLE_NAME} ({', '.join(columns)}) VALUES ({placeholders})"
    values = tuple(new_control.get(col) for col in columns)

    execute_query(query, values)

    # Update JSON file
    write_json(controls)

    return jsonify({"message": "Control added successfully", "control": new_control}), 201


# PUT - Update control
@app.route('/controls/<int:control_id>', methods=['PUT'])
def update_control(control_id):
    print(f"Received control_id: {control_id}")  # Debugging

    # Fetch the control from the database
    with sqlite3.connect(DB_PATH) as con:
        cursor = con.cursor()
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = ?", (control_id,))
        row = cursor.fetchone()

    if not row:
        print("Control not found in the database!")  # Debugging
        return jsonify({"message": "Control not found"}), 404

    # Convert row to dictionary
    columns = ["id"] + fetch_columns()  # Ensure "id" is included
    control = dict(zip(columns, row))
    print(f"Existing Control: {control}")  # Debugging

    # Get update data from request
    data = request.json
    print(f"Update Data: {data}")  # Debugging

    # Update the database
    set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
    query = f"UPDATE {TABLE_NAME} SET {set_clause} WHERE id = ?"
    values = tuple(data.values()) + (control_id,)

    try:
        execute_query(query, values)
    except Exception as e:
        return jsonify({"message": "Database update failed", "error": str(e)}), 500

    # Fetch updated control from the database
    with sqlite3.connect(DB_PATH) as con:
        cursor = con.cursor()
        cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = ?", (control_id,))
        updated_row = cursor.fetchone()

    updated_control = dict(zip(columns, updated_row))
    print(f"Updated Control: {updated_control}")  # Debugging

    # Load JSON data and update the control
    global controls
    controls = read_json()  # Reload the JSON to keep it fresh

    for i, c in enumerate(controls):
        if c["id"] == control_id:
            controls[i].update(updated_control)  # Update the control in JSON
            break

    # Write the updated data back to JSON
    write_json(controls)

    return jsonify({"message": "Control updated successfully", "control": updated_control})


# DELETE - Remove control
@app.route('/controls/<int:control_id>', methods=['DELETE'])
def delete_control(control_id):
    global controls

    # Check if control exists
    control = next((c for c in controls if c["id"] == control_id), None)
    if not control:
        return jsonify({"message": "Control not found"}), 404

    # Remove from JSON data
    controls = [c for c in controls if c["id"] != control_id]

    # Delete from SQLite
    execute_query(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (control_id,))

    # Update JSON file
    write_json(controls)

    return jsonify({"message": "Control deleted successfully"}), 200

# ------------------ Main ------------------

if __name__ == '__main__':
    app.run(debug=True)
