import requests
from flask import Flask, jsonify
from pymongo import MongoClient
from flask_cors import CORS
import os
from dotenv import load_dotenv

# Load environment variables (optional for secrets like MongoDB URI)
load_dotenv()

# Flask app setup
app = Flask(__name__)
CORS(app)

# MongoDB connection (localhost)
client = MongoClient("mongodb://localhost:27017")  # Local MongoDB connection string
db = client["f1_world_map"]  # Database name
circuits_collection = db["circuits"]  # Collection name

# Test route
@app.route("/")
def home():
    return jsonify({"message": "Welcome to the F1 World Map API!"})

# Fetch and store current circuits for 2024 from Ergast API
@app.route("/fetch-circuits", methods=["GET"])
def fetch_circuits():
    url = "http://ergast.com/api/f1/2024/circuits.json"
    response = requests.get(url)
    
    if response.status_code == 200:
        circuits_data = response.json()["MRData"]["CircuitTable"]["Circuits"]

        for circuit in circuits_data:
            circuit_entry = {
                "name": circuit["circuitName"],
                "location": circuit["Location"]["locality"],
                "country": circuit["Location"]["country"],
                "url": circuit["url"]
            }

            # Insert into MongoDB if not already present
            if not circuits_collection.find_one({"name": circuit_entry["name"]}):
                circuits_collection.insert_one(circuit_entry)
        
        return jsonify({"message": "Circuits for 2024 fetched and stored successfully!"}), 200
    else:
        return jsonify({"error": "Failed to fetch circuits from Ergast API"}), 500

# Get all circuits from the database
@app.route("/circuits", methods=["GET"])
def get_circuits():
    circuits = list(circuits_collection.find({}, {"_id": 0}))  # Exclude _id field
    return jsonify(circuits)

if __name__ == "__main__":
    app.run(debug=True)
