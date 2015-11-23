import logging
import dateutil.parser
from bson.objectid import ObjectId
from flask import Flask, request, abort, jsonify
from models import drivers, orders, odump

app = Flask(__name__)

def resource(model, id):
    if request.method == "PATCH":
        query = { "_id": ObjectId(id) }
        result = model.find_and_set(query, request.get_json())
    else:
        result = model.get(id)

    if not result:
        return abort(404)
    return odump(result)


@app.route('/drivers', methods=["POST"])
def add_driver():
    did = drivers.add(request.get_json())
    return jsonify(id=str(did))


@app.route('/drivers/<did>', methods=["GET", "PATCH"])
def driver(did):
    return resource(drivers, did)


@app.route('/orders', methods=["POST"])
def place_order():
    json = request.get_json()
    if "pickup_time" in json:
        json["pickup_time"] = dateutil.parser.parse(json["pickup_time"])
    oid = orders.add(json)
    return jsonify(id=str(oid))


@app.route('/orders/<oid>', methods=["GET", "PATCH"])
def order(oid):
    return resource(orders, oid)


def main_loop():
    app.run(debug=True)


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    main_loop()
