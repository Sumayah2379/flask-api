from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)
CORS(app)

# ✅ Root path to avoid 404 on Render
@app.route('/')
def home():
    return "✅ Flask API is up and running!"

client = MongoClient("mongodb://localhost:27017/")
db = client["userdb"]
collection = db["users"]

def serialize_user(user):
    return {
        "id": str(user["_id"]),
        "name": user["name"],
        "age": user["age"]
    }

@app.route('/users', methods=['GET'])
def get_users():
    users = [serialize_user(u) for u in collection.find()]
    return jsonify({"users": users})

@app.route('/users/<string:user_id>', methods=['GET'])
def get_user(user_id):
    try:
        user = collection.find_one({"_id": ObjectId(user_id)})
        if user:
            return jsonify({"user": serialize_user(user)})
        return jsonify({"error": "User not found"}), 404
    except:
        return jsonify({"error": "Invalid ID format"}), 400

@app.route('/users', methods=['POST'])
def add_user():
    data = request.json
    name = data.get("name")
    age = data.get("age")
    if not name or age is None:
        return jsonify({"error": "Name and Age are required"}), 400
    result = collection.insert_one({"name": name, "age": age})
    return jsonify({"message": "User added", "id": str(result.inserted_id)}), 201

@app.route('/users/<string:user_id>', methods=['DELETE'])
def delete_user(user_id):
    try:
        result = collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 1:
            return jsonify({"message": "User deleted"})
        return jsonify({"error": "User not found"}), 404
    except:
        return jsonify({"error": "Invalid ID format"}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)
