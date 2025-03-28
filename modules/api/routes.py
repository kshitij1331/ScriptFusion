from flask import Flask, jsonify, request, render_template
from flask_cors import CORS
import json
import sqlite3
import os

try:
    from config.variables import DB_NAME, TABLE_NAME, JSON_FILE, DATA_DIR
except ImportError:
    raise ImportError("⚠️ Missing required configuration: 'config/variables.py'. Ensure this file exists!")

from modules.api import api_bp

CORS(api_bp)

DB_PATH = os.path.join(DATA_DIR, DB_NAME)
JSON_PATH = os.path.join(DATA_DIR, JSON_FILE)


# ------------------ Utility Functions ------------------

def read_json():
    """Reads JSON data from file every time it's called."""
    try:
        if not os.path.exists(JSON_PATH):
            return []  # Return empty list if file doesn't exist
        with open(JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return []  # Return empty list if JSON is corrupt
    except Exception as e:
        print(f"⚠️ Unexpected error reading JSON: {str(e)}")
        return []

def write_json(data):
    """Writes updated JSON data to file."""
    try:
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except Exception as e:
        raise RuntimeError(f"⚠️ Failed to write JSON file: {str(e)}")


def get_next_db_id():
    """Fetches the next available ID from the SQLite database."""
    try:
        with sqlite3.connect(DB_PATH) as con:
            cursor = con.cursor()
            cursor.execute(f"SELECT MAX(id) FROM {TABLE_NAME}")
            max_id = cursor.fetchone()[0]
            return (max_id or 0) + 1  # Start from 1 if empty
    except sqlite3.Error as e:
        raise RuntimeError(f"⚠️ Database error fetching next ID: {str(e)}")


def fetch_columns():
    """Fetches column names dynamically from the table, excluding 'id'."""
    try:
        with sqlite3.connect(DB_PATH) as con:
            cursor = con.cursor()
            cursor.execute(f"PRAGMA table_info({TABLE_NAME})")
            columns = [col[1] for col in cursor.fetchall() if col[1] != "id"]
            if not columns:
                raise ValueError("⚠️ Table has no valid columns!")
            return columns
    except sqlite3.Error as e:
        raise RuntimeError(f"⚠️ Database error fetching columns: {str(e)}")


def execute_query(query, values=None, fetch_last_id=False):
    """Executes a SQL query with error handling."""
    try:
        with sqlite3.connect(DB_PATH) as con:
            cursor = con.cursor()
            cursor.execute(query, values or [])
            con.commit()
            return cursor.lastrowid if fetch_last_id else None
    except sqlite3.OperationalError as e:
        raise RuntimeError(f"⚠️ SQL error: {str(e)}")
    except sqlite3.Error as e:
        raise RuntimeError(f"⚠️ Database error: {str(e)}")


# Load JSON Data
try:
    controls = read_json()
except Exception as e:
    print(f"⚠️ Error loading JSON: {str(e)}")
    controls = []  # Default empty list

# ------------------ Routes ------------------

@api_bp.route('/')
def control_list():
    return render_template("control-list.html")


@api_bp.route('/controls', methods=['GET'])
def get_controls():
    """Returns all controls with error handling."""
    try:
        return jsonify(controls)
    except Exception as e:
        return jsonify({"error": f"⚠️ Error retrieving controls: {str(e)}"}), 500


@api_bp.route('/controls/<int:control_id>', methods=['GET'])
def get_control(control_id):
    """Fetches a single control by ID."""
    try:
        with sqlite3.connect(DB_PATH) as con:
            cursor = con.cursor()
            cursor.execute(f"SELECT * FROM {TABLE_NAME} WHERE id = ?", (control_id,))
            row = cursor.fetchone()

        if row:
            columns = ["id"] + fetch_columns()
            return jsonify(dict(zip(columns, row)))
        else:
            return jsonify({"error": "⚠️ Control not found"}), 404
    except sqlite3.Error as e:
        return jsonify({"error": f"⚠️ Database error: {str(e)}"}), 500


@api_bp.route('/controls', methods=['POST'])
def add_control():
    """Adds a new control entry."""
    try:
        global controls
        data = request.json
        if not data:
            return jsonify({"error": "⚠️ No data provided"}), 400

        new_id = get_next_db_id()
        new_control = {"id": new_id, **data}
        controls.append(new_control)

        # Insert into database
        columns = fetch_columns()
        placeholders = ", ".join(["?" for _ in columns])
        query = f"INSERT INTO {TABLE_NAME} ({', '.join(columns)}) VALUES ({placeholders})"
        values = tuple(new_control.get(col) for col in columns)

        execute_query(query, values)
        write_json(controls)

        return jsonify({"message": "✅ Control added successfully", "control": new_control}), 201

    except Exception as e:
        return jsonify({"error": f"⚠️ Failed to add control: {str(e)}"}), 500


@api_bp.route('/controls/<int:control_id>', methods=['PUT'])
def update_control(control_id):
    """Updates an existing control."""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "⚠️ No data provided"}), 400

        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        query = f"UPDATE {TABLE_NAME} SET {set_clause} WHERE id = ?"
        values = tuple(data.values()) + (control_id,)

        execute_query(query, values)

        # Reload JSON and update
        global controls
        controls = read_json()
        for c in controls:
            if c["id"] == control_id:
                c.update(data)
                break

        write_json(controls)
        return jsonify({"message": "✅ Control updated successfully"})

    except sqlite3.Error as e:
        return jsonify({"error": f"⚠️ Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"⚠️ Error updating control: {str(e)}"}), 500


@api_bp.route('/controls/<int:control_id>', methods=['DELETE'])
def delete_control(control_id):
    """Deletes a control entry."""
    try:
        global controls
        control = next((c for c in controls if c["id"] == control_id), None)
        if not control:
            return jsonify({"error": "⚠️ Control not found"}), 404

        controls = [c for c in controls if c["id"] != control_id]
        execute_query(f"DELETE FROM {TABLE_NAME} WHERE id = ?", (control_id,))
        write_json(controls)

        return jsonify({"message": "✅ Control deleted successfully"}), 200

    except sqlite3.Error as e:
        return jsonify({"error": f"⚠️ Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"⚠️ Error deleting control: {str(e)}"}), 500
