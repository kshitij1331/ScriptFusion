from flask import Flask, render_template,redirect, url_for
from modules.upload.routes import upload_bp
from modules.api import api_bp
import os
import sys
from modules import *
import subprocess

app = Flask(__name__)
app.secret_key = "supersecretkey"

# @app.route('/')
# def home():
#     return redirect(url_for("upload.index"))

print("running upload")
app.register_blueprint(upload_bp, url_prefix="/upload")
print("running api")
app.register_blueprint(api_bp, url_prefix="/api")

if __name__ == '__main__':
    print("Starting Full Service (Upload + API)...")
    # os.execv(sys.executable, ['python', 'main.py'])
    #subprocess.Popen([sys.executable, "main.py"])  # Run main.py as a separate process
    app.run(debug=True)
