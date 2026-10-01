from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from models import User
from models import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from config import Config
import re

jwt = JWTManager()

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
jwt.init_app(app)

EMAIL_REGEX = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]{2,}$")

def valid_email(email: str) -> bool:
    return bool(EMAIL_REGEX.match(email))

def valid_password(password: str) -> bool:
    return len(password) >= 8




REGISTER_FIELDS = ["forename", "surname", "email", "password"]

@app.route("/register", methods = ["POST"])
def register():
    data = request.get_json(silent=True) or {}

    for field in REGISTER_FIELDS:
        value = data.get(field)
        if not isinstance(value, str) or len(value) == 0:
            return jsonify({"message": f"Field {field} is missing."}), 400

    if not valid_email(data["email"]):
        return jsonify({"message" : "Invalid email."}), 400

    if not valid_password(data["password"]):
        return jsonify({"message" : "Invalid password."}), 400

    if User.query.filter_by(email = data["email"]).first():
        return jsonify({"message" : "Email already exists."}), 400

    user = User(
        forename = data["forename"],
        surname = data["surname"],
        email = data["email"],
        password_hash = generate_password_hash(data["password"]),
        role = "employee"
    )
    db.session.add(user)
    db.session.commit()

    return "", 200



LOGIN_FIELDS = ["email", "password"]

@app.route("/login", methods = ["POST"])
def login():
    data = request.get_json(silent = True) or {}

    for field in LOGIN_FIELDS:
        value = data.get(field)
        if not isinstance(value, str) or len(value) == 0:
            return jsonify({"message": f"Field {field} is missing."}), 400
        
    if not valid_email(data["email"]):
        return jsonify({"message": "Invalid email."}), 400

    user = User.query.filter_by(email = data["email"]).first()
    if not user or not check_password_hash(user.password_hash, data["password"]):
        return jsonify({"message": "Invalid credentials."}), 400
    
    additional_claims = {
        "forename": user.forename,
        "surname": user.surname,
        "email": user.email,
        "role": user.role
    }
    token = create_access_token(identity = user.email, additional_claims = additional_claims)

    return jsonify({"accessToken": token}), 200



@app.route("/delete", methods = ["POST"])
@jwt_required()
def delete():
    email = get_jwt_identity()
    user = User.query.filter_by(email = email).first()

    if not user:
        return jsonify({"message": "Unknown user."}), 400

    db.session.delete(user)
    db.session.commit()

    return "", 200


def init_director():
    email = "onlymoney@gmail.com"
    if not User.query.filter_by(email = email).first():
        director = User(
            forename = "Scrooge",
            surname = "McDuck",
            email = email,
            password_hash = generate_password_hash("evenmoremoney"),
            role = "director"
        )
        db.session.add(director)
        db.session.commit()

    
with app.app_context():
    db.create_all()
    init_director()

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = 5000)