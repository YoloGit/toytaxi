import json
import pymongo
import datetime
import os

from pymongo.collection import ReturnDocument
from bson.objectid import ObjectId

mongo = pymongo.MongoClient(host=os.environ.get("MONGO_HOST"), connect=False)
db = mongo.taxi
db.drivers.create_index([
    ("location", pymongo.GEO2D)
])
db.orders.create_index([
    ("status", pymongo.ASCENDING),
    ("pickup_time", pymongo.ASCENDING)
])


class BaseModel:
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

    def set(self, oid, fields):
        return self.collection.update_one(
            {"_id": ObjectId(oid)}, { "$set": fields }
        )


class Orders(BaseModel):
    collection = db.orders


class Drivers(BaseModel):
    collection = db.drivers


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
