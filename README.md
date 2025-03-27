# ScriptFusion

## Steps to Execute

1. Run `main.py` to generate the database and JSON files.
2. Run `app.py` to start the Flask API.
3. Open a browser and navigate to the given URL.
4. Use Postman or any API client to test the endpoints.

---

## File Descriptions

### `xlsx_to_sqlite3.py`
- Converts an Excel (`.xlsx`) file into an SQLite database.

### `sqlite3_to_json.py`
- Extracts data from the SQLite database and converts it into a JSON file.

### `main.py`
- Integrates both database creation and JSON conversion into a single execution.

### `variables.py`
- Contains required configurations to start the process.

### `app.py`
- A Flask-based API to serve the processed data.


---

## Directory Structure
```
ScriptFusion/
├── app.py
├── config/
│   └── variables.py
├── data/
│   ├── Benchmark.db
│   ├── CIS_Red_Hat_Enterprise_Linux_8_Benchmark_v3.0.0.xlsx
│   └── output.json
├── logs/
├── scripts/
│   ├── sqlite3_to_json.py
│   └── xlsx_to_sqlite3.py
├── static/
│   ├── assets/
│   ├── css/
│   │   └── styles.css
│   └── js/
│       └── script.js
├── templates/
│   └── index.html
├── main.py
└── Readme.md
```
