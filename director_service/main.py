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
from web3 import Web3
import time
import threading
import os

_dir = os.path.dirname(__file__)

with open(os.path.join(_dir, "output", "Voting.abi"), "r") as f:
    ABI = f.read()

with open(os.path.join(_dir, "output", "Voting.bin"), "r") as f:
    BYTECODE = f.read().strip()

app = Flask(__name__)
app.config.from_object(Config)

jwt = JWTManager(app)

mongo_client = MongoClient(Config.MONGO_URI)
db = mongo_client[Config.MONGO_DB_NAME]
assets = db["assets"]

redis_client = redis.Redis(host = Config.REDIS_HOST, port = Config.REDIS_PORT, decode_responses = True)

w3 = Web3(Web3.HTTPProvider(Config.GANACHE_URL))

def process_order(order):
    if order.get("order_type") == "BUY":
        assets.insert_one({
            "name": order.get("name"),
            "categories": order.get("categories"),
            "buying_price": order.get("buying_price"),
            "buying_date": datetime.now(),
            "info": order.get("info")
        })
    else:
        assets.update_one(
            {"_id": ObjectId(order.get("id"))}, 
            {"$set": {
                "selling_price": order.get("selling_price"), 
                "selling_date": datetime.now()
            }})

def serialize_transaction(transaction):
    result = {}
    for k, v in transaction.items():
        if isinstance(v, bytes):
            result[k] = "0x" + v.hex()
        elif hasattr(v, "hex"):
            result[k] = v.hex()
        else:
            result[k] = v
    return result

def voating_monitor():
    while True:
        try:
            for key in redis_client.scan_iter("contract:*"):
                entry = json.loads(redis_client.get(key))
                contract_address = entry["contract_address"]
                order_uuid = entry["uuid"]

                contract = w3.eth.contract(address = contract_address, abi = ABI)
                ended = contract.functions.ended().call()

                if ended:
                    order_data = json.loads(redis_client.get(f"order:{order_uuid}"))
                    if contract.functions.approved().call():
                        process_order(order_data)
                    
                    redis_client.delete(f"order:{order_uuid}")
                    redis_client.delete(key)
                
        except Exception as e:
            print(f"Monitor error: {e}")
        
        time.sleep(2)

threading.Thread(target = voating_monitor, daemon = True).start()


@app.route("/pending_orders", methods = ["GET"])
@role_check("director")
def pending_orders():
    orders = []

    for key in redis_client.scan_iter(match = "order:*"):
        order = json.loads(redis_client.get(key))
        order["uuid"] = key.removeprefix("order:")
        orders.append(order)

    return jsonify({"orders": orders}), 200

@app.route("/decision", methods = ["POST"])
@role_check("director")
def decision():
    data = request.get_json(silent = True) or {}

    id = data.get("uuid")
    if not isinstance(id, str) or len(id) == 0:
        return jsonify({"message": "Field uuid is missing."}), 400
    
    try:
        uuid.UUID(id)
    except ValueError:
        return jsonify({"message": "Invalid uuid."}), 400
    
    order = redis_client.get(f"order:{id}")
    if order is None:
        return jsonify({"message": "Invalid uuid."}), 400

    voters = data.get("voters")
    if not voters or len(voters) == 0:
        return jsonify({"message": "Field voters is missing."}), 400
    
    for address in voters:
        if not w3.is_address(address):
            return jsonify({"message": "Invalid voter address."}), 400
        
    if len(voters) % 2 == 0:
        return jsonify({"message": "Even number of voters."}), 400
    
    contract = w3.eth.contract(abi = ABI, bytecode = BYTECODE)
    checksum_voters = [w3.to_checksum_address(v) for v in voters]

    transaction_hash = contract.constructor(checksum_voters).transact({
        "from": w3.eth.accounts[0],
        "gas": 3000000
    })
    receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
    contract_address = receipt["contractAddress"]
    
    redis_client.set(
        f"contract:{id}",
        json.dumps({"contract_address": contract_address, "uuid": id})
    )

    deployed = w3.eth.contract(address = contract_address, abi = ABI)
    transaction_base = {
        "chainId": w3.eth.chain_id,
        "gas": 200000,
        "gasPrice": w3.eth.gas_price
    }
    approve_transaction = deployed.functions.voteApprove().build_transaction(transaction_base)
    reject_transaction = deployed.functions.voteReject().build_transaction(transaction_base)

    for transaction in (approve_transaction, reject_transaction):
        transaction.pop("from", None)
        transaction.pop("nonce", None)

    return jsonify({"approve_transaction": serialize_transaction(approve_transaction), 
                    "reject_transaction": serialize_transaction(reject_transaction)})


@app.route("/report", methods = ["GET"])
@role_check("director")
def report():

    pipeline = [
        {"$unwind": "$categories"},
        {
            "$group": {
                "_id": "$categories",
                "spent": {"$sum": "$buying_price"},
                "earned": {
                    "$sum": {
                        "$cond": [
                            {"$ifNull": ["$selling_date", False]},
                            "$selling_price",
                            0
                        ]
                    }
                }
            }
        },
        {
            "$project": {
                "_id": 0,
                "category": "$_id",
                "spent": 1,
                "earned": 1
            }
        },
        {
            "$sort": {"earned": -1, "spent": 1, "category": 1}
        }
    ]

    result = list(assets.aggregate(pipeline))

    return jsonify({"statistics": result}), 200


if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 5000)