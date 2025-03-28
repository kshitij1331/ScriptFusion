from flask import Blueprint

# Define the Blueprint
api_bp = Blueprint("api", __name__, template_folder="../../templates")

# Import the routes (This must be at the bottom to avoid circular import issues)
from modules.api import routes