# ScriptFusion

## Steps to Execute

1. Run `app.py` to start the Flask app.
2. Open the webpage in your browser.
3. Upload your Excel file.
4. Click on the **Submit** button.
5. To convert your Excel file into JSON, click on the **Run Script** button.
6. Click on the **Proceed** button to be redirected to the controls list page.  
7. Now you will see the controls listed. You can now perform further operations.

---

## File Descriptions

### Project Structure

```
ScriptFusion/
├── app.py
├── config/
│   └── variables.py
├── deletecache.sh
├── main.py
├── modules/
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   └── upload/
│      ├── __init__.py
│      └── routes.py
├── scripts/
│   ├── __init__.py
│   ├── sqlite3_to_json.py
│   └── xlsx_to_sqlite3.py
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── images/
│   │   └── fusion.jfif
│   └── js/
│        └── script.js
├── templates/
│   ├── control-list.html
│   ├── index.html
│   └── uploadfile.html
└── README.md
```

### Script Descriptions

- **`xlsx_to_sqlite3.py`** → Converts an Excel (`.xlsx`) file into an SQLite database.
- **`sqlite3_to_json.py`** → Extracts data from the SQLite database and converts it into a JSON file.
- **`main.py`** → Integrates both database creation and JSON conversion into a single execution.
- **`variables.py`** → Contains required configurations to start the process.
- **`app.py`** → A Flask-based API to serve the processed data.
- **`deletecache.sh`** → A shell script to clear cache or temporary files.

---
