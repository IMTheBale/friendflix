from db.db import get_db
from flask import Blueprint, request
from flask_jwt_extended import create_access_token, get_jwt, jwt_required
from models.auth import User
from werkzeug.security import generate_password_hash

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    cursor = get_db().cursor()
    user = User.get_by_login(username, password, cursor)
    if user is None:
        return "Invalid username or password", 401
    return {"token": create_access_token(identity=user.id, additional_claims=user.asdict())}


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    secure_password = generate_password_hash(password)
    cursor = get_db().cursor()
    columns = User.fields(as_columns=True)
    cursor.execute(
        f"INSERT INTO users (username, email, password) VALUES (?, ?, ?) RETURNING {columns}",
        [username, email, secure_password],
    )
    cursor.connection.commit()
    new_user = User.from_sql_row(cursor.fetchone())
    return new_user.asdict() if new_user else {}


@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():
    user = get_jwt()
    cursor = get_db().cursor()
    cursor.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", user["id"])
    cursor.connection.commit()
    return ""


@auth_bp.route("/register/check")
def register_check():
    username = request.args.get("username")
    cursor = get_db().cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", [username])
    response_code = 200 if cursor.fetchone() is None else 409
    return "", response_code


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    return "Forgot password", 501
