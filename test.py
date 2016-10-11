import requests
from flask import Flask, jsonify
from flask import json

app = Flask(__name__)

@app.route("/")
def index():
    data = requests.get("https://api.spotcrime.com/crimes.json?lat=37.334164&lon=-121.884301&radius=0.02&key=.")
    data = data.json()
    response = {}
    total_crimes = len(data["crimes"])
    response["total_crimes"] = total_crimes
    return response

app.run(debug=True, port=5000, host="0.0.0.0")