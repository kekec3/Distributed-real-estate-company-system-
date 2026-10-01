from flask import Flask
from flask import request
from flask import jsonify
from flask_jwt_extended import JWTManager
from pymongo import MongoClient
import redis
from config import Config
from datetime import datetime
from bson import ObjectId
import json
import uuid
from bson.errors import InvalidId
from decorators import role_check

app = Flask(__name__)
app.config.from_object(Config)

jwt = JWTManager(app)

mongo_client = MongoClient(Config.MONGO_URI)
db = mongo_client[Config.MONGO_DB_NAME]
assets = db["assets"]

redis_client = redis.Redis(host = Config.REDIS_HOST, port = Config.REDIS_PORT, decode_responses = True)

def from_iso(date: str) -> datetime:
    return datetime.fromisoformat(date.replace("Z", "+00:00"))

def to_iso(date: datetime) -> str:
    return date.strftime("%Y-%m-%dT%H:%M:%S.") + f"{date.microsecond // 1000:03d}Z"

@app.route("/search", methods = ["POST"])
@role_check("employee")
def search():
    data = request.get_json(silent = True) or {}
    query = {}

    name = data.get("name")
    if name:
        query["name"] = {"$regex": name, "$options": "i"}

    category = data.get("category")
    if category:
        query["categories"] = category

    buying_data = data.get("buying_date")
    if buying_data:
        query["buying_date"] = {"$gt": from_iso(buying_data)}

    selling_date = data.get("selling_date")
    if selling_date:
        query["selling_date"] = {"$exists": True, "$lte": from_iso(selling_date)}

    for filter in data.get("info_filters", []):
        field = filter.get("field")
        operator = filter.get("operator")
        value = filter.get("value")
        query[f"info.{field}"] = {f"${operator}": value}

    results = []
    for doc in assets.find(query):
        item = {
            "id": str(doc["_id"]),
            "name": doc["name"],
            "categories":   doc["categories"],
            "buying_date":  to_iso(doc["buying_date"]),
            "buying_price": doc["buying_price"],
            "info":         doc.get("info", {})
        }
        if "selling_date" in doc:
            item["selling_date"] = to_iso(doc["selling_date"])
            item["selling_price"] = doc["selling_price"]

        results.append(item)

    return jsonify({"assets": results}), 200

@app.route("/create_buy_order", methods = ["POST"])
@role_check("employee")
def create_buy_order():
    data = request.get_json(silent = True) or {}

    name = data.get("name")
    if not isinstance(name, str) or len(name) == 0:
        return jsonify({"message": "Field name is missing."}), 400
    
    categories = data.get("categories")
    if not isinstance(categories, list):
        return jsonify({"message": "Field categories is missing."}), 400
    
    buying_price = data.get("buying_price")
    if buying_price is None:
        return jsonify({"message": "Field buying_price is missing."}), 400

    info = data.get("info")
    if info is None:
        return jsonify({"message": "Field info is missing."}), 400
    
    if len(categories) == 0:
        return jsonify({"message": "Categories list is empty."}), 400

    if not isinstance(buying_price, (int, float)) or buying_price <= 0:
        return jsonify({"message": "Invalid buying price."}), 400
    
    order_id = str(uuid.uuid4())
    order = {
        "order_type": "BUY",
        "name": name,
        "categories": categories,
        "buying_price": buying_price,
        "info": info
    }

    redis_client.set(f"order:{order_id}", json.dumps(order))

    return "", 200

@app.route("/create_sell_order", methods = ["POST"])
@role_check("employee")
def create_sell_order():
    data = request.get_json(silent = True) or {}

    id = data.get("id")
    if not isinstance(id, str) or len(id) == 0:
        return jsonify({"message": "Field id is missing."}), 400
    
    selling_price = data.get("selling_price")
    if selling_price is None:
        return jsonify({"message": "Field selling_price is missing."}), 400
    
    try:
        obj_id = ObjectId(id)
    except (InvalidId, Exception):
        return jsonify({"message": "Invalid id."}), 400
    
    if not assets.find_one({"_id": obj_id}):
        return jsonify({"message": "Invalid id."}), 400
    
    if not isinstance(selling_price, (int, float)) or selling_price <= 0:
        return jsonify({"message": "Invalid selling price."}), 400
    
    order_id = str(uuid.uuid4())
    order = {
        "order_type": "SELL",
        "id": id,
        "selling_price": selling_price
    }

    redis_client.set(f"order:{order_id}", json.dumps(order))

    return "", 200

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 5000)