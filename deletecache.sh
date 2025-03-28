find . -name __pycache__ -type d -exec rm -rf '{}' +
rm -rf data/*
echo """EXCEL_NAME = ''
SUBSHEET_NAME = ''
DB_NAME = ''
TABLE_NAME = ''
JSON_FILE = 'output.json'
DATA_DIR = 'data'""" > config/variables.py
echo "Deleted cache successfully"
