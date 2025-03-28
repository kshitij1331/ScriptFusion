from flask import Flask, render_template, jsonify
from modules.upload import upload_bp  # Import the correct Blueprint
from modules.api import api_bp

app = Flask(__name__)
app.secret_key = "supersecretkey"

app.register_blueprint(upload_bp, url_prefix="/upload")
app.register_blueprint(api_bp, url_prefix="/api")

@app.route('/')
def home():
    return render_template("index.html")

if __name__ == '__main__':
    print("🚀 Starting Upload Service...")
    app.run(debug=True)
