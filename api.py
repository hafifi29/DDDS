from database import register_user, initialize_users_table, login_user
from flask import Flask, request, jsonify, session
import bcrypt

app = Flask(__name__)
app.secret_key = "super_secret_key_0123456789"

@app.route("/register", methods=["POST"])
def register():
    """Endpoint to register a new user."""

    request_body = request.json
    username = request_body.get("username")
    password = request_body.get("password")
    fullname = request_body.get("fullname")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    hashed_password = bcrypt.hashpw(password.encode("UTF-8"), bcrypt.gensalt())

    registration_result = register_user(username, hashed_password, fullname)

    if registration_result:
        return jsonify({"message": "User registered successfully"}), 201

    else:
        return jsonify({"error": "Username already exists"}), 400


@app.route("/login", methods=["POST"])
def login():
    """Endpoint to log in a user."""

    request_body = request.json
    username = request_body.get("username")
    password = request_body.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    login_result = login_user(username, password)

    if login_result:
        session["username"] = username
        return jsonify({"message": f"User logged in successfully",
                        "username": username}), 200

    else:
        return jsonify({"error": "Invalid username or password"}), 401

@app.route("/logout", methods=["POST"])
def logout():
    """Endpoint to log out a user."""
    session.pop("username", None)
    return jsonify({"message": "User logged out successfully"}), 200

def get_login_status():
    """Check if a user is logged in and return the status."""

    with app.test_request_context():
        if "username" in session:
            return {"logged_in": True, "username": session["username"]}

        else:
            return {"logged_in": False}

if __name__ == "__main__":
    initialize_users_table()
    app.run(host="0.0.0.0", port=5000)