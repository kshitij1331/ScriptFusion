from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
import os
from modules.upload import upload_bp  
import subprocess
import sys

# Ensure config directory exists
CONFIG_DIR = "config"
os.makedirs(CONFIG_DIR, exist_ok=True)

VARIABLES_FILE = os.path.join(CONFIG_DIR, "variables.py")

# Ensure data directory exists
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Set Upload Folder for the Blueprint
UPLOAD_FOLDER = "data"

@upload_bp.route('/')
def index():
    print("Serving index.html...")  # Debug log
    return render_template("uploadfile.html")

@upload_bp.route('/uploadfile', methods=['POST'])
def upload_file():
    file = request.files.get("file")
    
    subsheet_name = request.form.get("subsheet_name") or "Sheet1"
    db_name = request.form.get("db_name") or "Benchmark.db"

    if not file or file.filename == "":
        flash("No file selected")
        return redirect(url_for("upload.index"))  # Updated to use the correct Blueprint name

    # Save file in data directory
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(file_path)

    # Update variables.py dynamically
    with open(VARIABLES_FILE, "w") as f:
        f.write(f"EXCEL_NAME = '{file.filename}'\n")
        f.write(f"SUBSHEET_NAME = '{subsheet_name}'\n")
        f.write(f"DB_NAME = '{db_name}'\n")
        f.write(f"TABLE_NAME = '{file.filename.split('.')[0].replace(' ', '_').replace('-', '_')}'\n")
        f.write(f"JSON_FILE = 'output.json'\n")
        f.write(f"DATA_DIR = 'data'\n")

    flash("File uploaded and configuration updated successfully!")
    return redirect(url_for("upload.index"))  # Corrected redirect to Blueprint route


@upload_bp.route('/run-script', methods=['POST'])
def run_script():
    try:
        result = subprocess.run(["python", "main.py"], capture_output=True, text=True, check=True)
        return jsonify({"status": "success", "output": result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({"status": "error", "message": e.stderr})