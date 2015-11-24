import logging
import dateutil.parser
from flask import Flask, request, abort, jsonify
from models import drivers, orders, odump

app = Flask(__name__)

def resource(model, id):
    """Common resource wrapper for driver and order"""

    if request.method == "PATCH":
        model.set(id, request.get_json())

    result = model.get(id)
    if not result:
        return abort(404)
    return odump(result)


@app.route('/drivers', methods=["POST", "DELETE"])
def add_driver():
    if request.method == "POST":
        did = drivers.add(request.get_json())
        return jsonify(id=str(did))

    elif request.method == "DELETE":
        drivers.remove_all()
        return jsonify()


@app.route('/drivers/<did>', methods=["GET", "PATCH"])
def driver(did):
    return resource(drivers, did)


@app.route('/orders', methods=["POST", "DELETE"])
def place_order():
    if request.method == "POST":
        json = request.get_json()
        if "pickup_time" in json:
            json["pickup_time"] = dateutil.parser.parse(json["pickup_time"])
        oid = orders.add(json)
        return jsonify(id=str(oid))

    elif request.method == "DELETE":
        orders.remove_all()
        return jsonify()


@app.route('/orders/<oid>', methods=["GET", "PATCH"])
def order(oid):
    return resource(orders, oid)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app.run(debug=True)
