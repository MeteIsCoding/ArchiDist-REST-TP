from flask import Flask, request, jsonify, make_response
import requests
import json
import time

app = Flask(__name__)

PORT = 3203
HOST = '0.0.0.0'

BOOKING_URL = "http://localhost:3201"

with open('./databases/users.json', 'r') as jsf:
    users = json.load(jsf)["users"]


def write():
    with open('./databases/users.json', 'w') as f:
        json.dump({"users": users}, f, indent=2)


##### check if the user who makes the request is admin #####
def is_admin():
    admin = request.args.get("admin", "")
    for user in users:
        if user["id"] == admin:
            return user["admin"]
    return False


@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the User service!</h1>"


##### get all users (admin) #####
@app.route("/json", methods=['GET'])
def get_json():
    if not is_admin():
        return make_response(jsonify({"error": "admin only"}), 403)

    return make_response(jsonify(users), 200)


##### get one user #####
@app.route("/users/<userid>", methods=['GET'])
def get_user(userid):
    for user in users:
        if user["id"] == userid:
            return make_response(jsonify(user), 200)

    return make_response(jsonify({"error": "user not found"}), 404)


##### add user (admin) #####
@app.route("/users/<userid>", methods=['POST'])
def add_user(userid):
    if not is_admin():
        return make_response(jsonify({"error": "admin only"}), 403)

    req = request.get_json()

    if "name" not in req:
        return make_response(jsonify({"error": "name missing"}), 400)

    for user in users:
        if user["id"] == userid:
            return make_response(jsonify({"error": "user already exists"}), 409)

    new_user = {
        "id": userid,
        "name": req["name"],
        "last_active": int(time.time()),
        "admin": req.get("admin", False)
    }

    users.append(new_user)
    write()

    return make_response(jsonify(new_user), 201)


##### update user (admin) #####
@app.route("/users/<userid>", methods=['PUT'])
def update_user(userid):
    if not is_admin():
        return make_response(jsonify({"error": "admin only"}), 403)

    req = request.get_json()

    for user in users:
        if user["id"] == userid:
            if "name" in req:
                user["name"] = req["name"]
            if "admin" in req:
                user["admin"] = req["admin"]

            write()
            return make_response(jsonify(user), 200)

    return make_response(jsonify({"error": "user not found"}), 404)


##### delete user (admin) #####
@app.route("/users/<userid>", methods=['DELETE'])
def delete_user(userid):
    if not is_admin():
        return make_response(jsonify({"error": "admin only"}), 403)

    for user in users:
        if user["id"] == userid:
            users.remove(user)
            write()
            return make_response(jsonify(user), 200)

    return make_response(jsonify({"error": "user not found"}), 404)


##### get user with bookings and movie details #####
@app.route("/users/<userid>/bookings", methods=['GET'])
def get_user_bookings(userid):
    for user in users:
        if user["id"] == userid:
            res = requests.get(BOOKING_URL + "/bookings/" + userid + "/details")

            bookings = []
            if res.status_code == 200:
                bookings = res.json()["dates"]

            return make_response(jsonify({
                "userid": userid,
                "name": user["name"],
                "bookings": bookings
            }), 200)

    return make_response(jsonify({"error": "user not found"}), 404)


if __name__ == "__main__":
    print("Port %s" % PORT)
    app.run(host=HOST, port=PORT)
