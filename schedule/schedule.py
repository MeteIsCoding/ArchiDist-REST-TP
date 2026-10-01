from flask import Flask, request, jsonify, make_response
import requests
import json

app = Flask(__name__)

PORT = 3202
HOST = '0.0.0.0'

MOVIE_URL = "http://localhost:3200"

with open('./databases/times.json', 'r') as jsf:
    schedule = json.load(jsf)["schedule"]


def write():
    with open('./databases/times.json', 'w') as f:
        json.dump({"schedule": schedule}, f, indent=2)


@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the Showtime service!</h1>"


##### get schedules #####
@app.route("/json", methods=['GET'])
def get_json():
    return make_response(jsonify(schedule), 200)


##### get schedule for one date #####
@app.route("/schedule/<date>", methods=['GET'])
def get_schedule(date):
    for item in schedule:
        if item["date"] == date:
            return make_response(jsonify(item), 200)

    return make_response(jsonify({"error": "date not found"}), 404)


##### add date #####
@app.route("/schedule/<date>", methods=['POST'])
def add_schedule(date):
    req = request.get_json()

    if "movies" not in req:
        return make_response(jsonify({"error": "movies missing"}), 400)

    for item in schedule:
        if item["date"] == date:
            return make_response(jsonify({"error": "date already exists"}), 409)

    new_item = {
        "date": date,
        "movies": req["movies"]
    }

    schedule.append(new_item)
    write()

    return make_response(jsonify(new_item), 201)


##### delete date #####
@app.route("/schedule/<date>", methods=['DELETE'])
def delete_schedule(date):
    for item in schedule:
        if item["date"] == date:
            schedule.remove(item)
            write()
            return make_response(jsonify(item), 200)

    return make_response(jsonify({"error": "date not found"}), 404)


##### schedule with movie information #####
@app.route("/schedule/<date>/details", methods=['GET'])
def get_schedule_details(date):
    for item in schedule:
        if item["date"] == date:
            result = {
                "date": date,
                "movies": []
            }

            for movieid in item["movies"]:
                try:
                    response = requests.get(
                        MOVIE_URL + "/movies/" + movieid
                    )

                    if response.status_code == 200:
                        result["movies"].append(response.json())

                except requests.RequestException:
                    return make_response(
                        jsonify({"error": "movie service unavailable"}),
                        503
                    )

            return make_response(jsonify(result), 200)

    return make_response(jsonify({"error": "date not found"}), 404)


if __name__ == "__main__":
    print("Port %s" % PORT)
    app.run(host=HOST, port=PORT)