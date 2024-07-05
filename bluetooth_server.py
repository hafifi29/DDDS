import bluetooth
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/login", methods=["POST"])
def login():
    request_body = request.json
    username = request_body.get("username")
    password = request_body.get("password")

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    login_result = login_user(username, password)

    if login_result:
        return jsonify({"message": f"User '{username}' logged in successfully"}), 200
    else:
        return jsonify({"error": "Invalid username or password"}), 401

def login_user(username, password):
    # Add your user authentication logic here
    return username == "admin" and password == "password"

def bluetooth_server():
    server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    port = 1
    server_sock.bind(("", port))
    server_sock.listen(1)
    client_sock, address = server_sock.accept()
    print("Accepted connection from ", address)

    while True:
        try:
            data = client_sock.recv(1024)
            if len(data) == 0:
                break
            print("received [%s]" % data)

            # Parse data and send to Flask
            with app.test_request_context('/login', method='POST', json={"username": "admin", "password": "password"}):
                response = login()
                client_sock.send(response.get_data())
        except IOError:
            break

    client_sock.close()
    server_sock.close()

if __name__ == "__main__":
    bluetooth_server()
