import scripts.xlsx_to_sqlite3
import scripts.sqlite3_to_json
from config.variables import EXCEL_NAME, DB_NAME, TABLE_NAME, JSON_FILE, SUBSHEET_NAME

scripts.xlsx_to_sqlite3.xlsx_to_sqlite(EXCEL_NAME, SUBSHEET_NAME, DB_NAME, TABLE_NAME)
scripts.sqlite3_to_json.sqlite_to_json(DB_NAME, TABLE_NAME, JSON_FILE)