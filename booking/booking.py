from flask import Flask, request, jsonify, make_response
import requests
import json

app = Flask(__name__)

PORT = 3201
HOST = '0.0.0.0'

with open('./databases/bookings.json', 'r') as jsf:
    bookings = json.load(jsf)["bookings"]


def write():
    with open('./databases/bookings.json', 'w') as f:
        json.dump({"bookings": bookings}, f, indent=2)


@app.route("/", methods=['GET'])
def home():
    return "<h1 style='color:blue'>Welcome to the Booking service!</h1>"


##### Get bookings for one user #####
@app.route("/bookings/<userid>", methods=['GET'])
def get_booking(userid):
    for booking in bookings:
        if booking["userid"] == userid:
            return make_response(jsonify(booking), 200)

    return make_response(jsonify({"error": "user not found"}), 404)


##### add boking #####
@app.route("/bookings/<userid>", methods=['POST'])
def add_booking(userid):
    req = request.get_json()
    date = req["date"]
    movieid = req["movieid"]

    ##### chekc if movie scheduled #####
    res = requests.get("http://localhost:3202/schedule/" + date)

    if res.status_code != 200:
        return make_response(jsonify({"error": "date not found"}), 404)

    if movieid not in res.json()["movies"]:
        return make_response(jsonify({"error": "movie not scheduled"}), 400)

    ##### find user #####
    for booking in bookings:
        if booking["userid"] == userid:

            ##### find date #####
            for day in booking["dates"]:
                if day["date"] == date:
                    if movieid in day["movies"]:
                        return make_response(
                            jsonify({"error": "already booked"}), 400
                        )

                    day["movies"].append(movieid)
                    write()
                    return make_response(jsonify(booking), 200)

            ##### new date #####
            booking["dates"].append({
                "date": date,
                "movies": [movieid]
            })

            write()
            return make_response(jsonify(booking), 200)

    ##### new user #####
    new_booking = {
        "userid": userid,
        "dates": [{
            "date": date,
            "movies": [movieid]
        }]
    }

    bookings.append(new_booking)
    write()

    return make_response(jsonify(new_booking), 200)


##### delete booking #####
@app.route("/bookings/<userid>/<date>/<movieid>", methods=['DELETE'])
def delete_booking(userid, date, movieid):
    for booking in bookings:
        if booking["userid"] == userid:

            for day in booking["dates"]:
                if day["date"] == date and movieid in day["movies"]:
                    day["movies"].remove(movieid)
                    write()

                    return make_response(
                        jsonify({"message": "booking deleted"}), 200
                    )

    return make_response(jsonify({"error": "booking not found"}), 404)


##### get bookings with movie details #####
@app.route("/bookings/<userid>/details", methods=['GET'])
def get_details(userid):
    for booking in bookings:
        if booking["userid"] == userid:
            result = []

            for day in booking["dates"]:
                movies = []

                for movieid in day["movies"]:
                    res = requests.get(
                        "http://localhost:3200/movies/" + movieid
                    )

                    if res.status_code == 200:
                        movies.append(res.json())

                result.append({
                    "date": day["date"],
                    "movies": movies
                })

            return make_response(jsonify({
                "userid": userid,
                "dates": result
            }), 200)

    return make_response(jsonify({"error": "user not found"}), 404)


if __name__ == "__main__":
    print("Port %s" % PORT)
    app.run(host=HOST, port=PORT)