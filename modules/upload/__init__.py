from flask import Blueprint

# Define the Blueprint
upload_bp = Blueprint("upload", __name__, template_folder="../../templates")

# Import the routes (This must be at the bottom to avoid circular import issues)
from modules.upload import routes