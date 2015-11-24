import json
import pymongo
import datetime
import os

from pymongo.collection import ReturnDocument
from bson.objectid import ObjectId

mongo = pymongo.MongoClient(host=os.environ.get("MONGO_HOST"), connect=False)
db = mongo.taxi

db.drivers.create_index([
    ("location", pymongo.GEO2D),
    ("order", pymongo.ASCENDING)
])

db.orders.create_index([
    ("status", pymongo.ASCENDING),
    ("pickup_time", pymongo.ASCENDING)
])


class BaseModel:
    """Just a tiny wrapper for Mongo queries"""

    def find_and_set(self, query, updates, sort=None):
        """Atomically find and update document"""
        return self.collection.find_one_and_update(
            query, { "$set": updates },
            return_document=ReturnDocument.AFTER,
            sort=sort
        )

    def add(self, obj):
        return self.collection.insert_one(obj).inserted_id

    def get(self, oid):
        return self.collection.find_one({"_id": ObjectId(oid)})

    def on_set(self, objectid, fields):
        pass

    def set(self, oid, fields):
        objectid = ObjectId(oid)
        self.collection.update_one({"_id": objectid}, { "$set": fields })
        self.on_set(objectid, fields)

    def remove_all(self):
        return self.collection.delete_many({})


class Orders(BaseModel):
    collection = db.orders

    def pick(self):
        """Atomically pick next order for processing"""
        return self.find_and_set(
            {
                "status": "new",
                "$or": [
                    { "pickup_time": { "$lte": datetime.datetime.now() } },
                    { "pickup_time": None }
                ]
            },
            { "status": "processing" },
            sort=[("pickup_time", 1)]
        )

    def on_set(self, objectid, fields):
        status = fields.get("status")
        if  status == "completed" or status == "canceled":
            drivers.free(objectid)


class Drivers(BaseModel):
    collection = db.drivers

    def pick(self, order):
        """Atomically find available driver, assign order"""
        return self.find_and_set(
            { "order": None, "location": {"$near": order["location"]} },
            { "order": order["_id"] }
        )

    def free(self, order_objectid):
        return self.find_and_set(
            { "order": order_objectid },
            { "order": None }
        )


orders = Orders()
drivers = Drivers()


class JSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        elif isinstance(o, datetime.datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


def odump(obj):
    return JSONEncoder().encode(obj)
