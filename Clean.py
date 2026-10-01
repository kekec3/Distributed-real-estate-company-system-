# reset.py
import pymysql
import pymongo
import redis
import sys
import time

MYSQL_HOST     = "localhost"
MYSQL_PORT     = 3306
MYSQL_USER     = "root"
MYSQL_PASSWORD = "rootpass"
MYSQL_DB       = "authdb"

MONGO_URI      = "mongodb://localhost:27017"
MONGO_DB       = "fundb"

REDIS_HOST     = "localhost"
REDIS_PORT     = 6379

errors = []

# ── Redis FIRST ──────────────────
print("Clearing Redis...")
try:
    r = redis.Redis(
        host=REDIS_HOST, port=REDIS_PORT,
        decode_responses=True, socket_connect_timeout=5
    )
    r.ping()

    order_keys    = list(r.scan_iter("order:*"))
    contract_keys = list(r.scan_iter("contract:*"))
    all_keys      = order_keys + contract_keys

    if all_keys:
        r.delete(*all_keys)

    remaining_orders    = list(r.scan_iter("order:*"))
    remaining_contracts = list(r.scan_iter("contract:*"))

    if remaining_orders or remaining_contracts:
        errors.append(f"Redis: {len(remaining_orders)} order(s) and {len(remaining_contracts)} contract(s) still remain!")
    else:
        print(f"  OK — deleted {len(order_keys)} order(s), {len(contract_keys)} contract(s).")

except Exception as e:
    errors.append(f"Redis connection failed: {e}")

# ── Wait for monitor thread to finish its current cycle ───────────────────────
if not errors:
    print("Waiting 5s for monitor thread to complete current cycle...")
    time.sleep(5)

# ── MongoDB SECOND ─────────────────
print("Clearing MongoDB...")
try:
    client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=5000)
    db = client[MONGO_DB]
    
    # Target all collections in fundb except system collections
    collections = db.list_collection_names()
    total_deleted = 0
    
    for col_name in collections:
        col = db[col_name]
        res = col.delete_many({})
        total_deleted += res.deleted_count

    client.close()
    print(f"  OK — cleared {len(collections)} collection(s), deleted {total_deleted} document(s) total.")

except Exception as e:
    errors.append(f"MongoDB connection failed: {e}")

# ── MySQL LAST ─────────────────────────────────────────
print("Clearing MySQL...")
try:
    conn = pymysql.connect(
        host=MYSQL_HOST, port=MYSQL_PORT,
        user=MYSQL_USER, password=MYSQL_PASSWORD,
        database=MYSQL_DB, connect_timeout=5
    )
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE email != 'onlymoney@gmail.com';")
    conn.commit()
    deleted = cursor.rowcount

    cursor.execute("SELECT COUNT(*) FROM users WHERE email != 'onlymoney@gmail.com';")
    remaining = cursor.fetchone()[0]
    cursor.close()
    conn.close()

    if remaining > 0:
        errors.append(f"MySQL: {remaining} non-director user(s) still remain!")
    else:
        print(f"  OK — deleted {deleted} user(s), director preserved.")

except Exception as e:
    errors.append(f"MySQL connection failed: {e}")

# ── Result ────────────────────────────────────────────────────────────────────
print()
if errors:
    print("RESET FAILED:")
    for err in errors:
        print(f"  x {err}")
    sys.exit(1)
else:
    print("Done. System is clean.")