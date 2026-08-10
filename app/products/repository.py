from datetime import datetime, timezone
from typing import Any

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING, MongoClient, ReturnDocument

from app.core import settings


class ProductRepository:
    """Acesso aos produtos armazenados exclusivamente no MongoDB."""

    def __init__(self):
        self.client = MongoClient(settings.mongo_url, serverSelectionTimeoutMS=5000)
        self.collection = self.client[settings.mongo_db]["products"]
        self.collection.create_index([("created_at", DESCENDING)])
        self.collection.create_index([("name", ASCENDING)])

    @staticmethod
    def _serialize(document: dict[str, Any] | None):
        if document is None:
            return None
        return {
            "id": str(document["_id"]),
            "name": document["name"],
            "description": document.get("description", ""),
            "price": document["price"],
            "status": document["status"],
            "created_at": document["created_at"],
        }

    def create(self, data: dict[str, Any]):
        document = dict(data)
        document["price"] = float(document["price"])
        document["created_at"] = datetime.now(timezone.utc)
        result = self.collection.insert_one(document)
        return self._serialize(self.collection.find_one({"_id": result.inserted_id}))

    def list(self):
        cursor = self.collection.find().sort("created_at", DESCENDING)
        return [self._serialize(document) for document in cursor]

    def get(self, product_id: str):
        if not ObjectId.is_valid(product_id):
            return None
        return self._serialize(self.collection.find_one({"_id": ObjectId(product_id)}))

    def update(self, product_id: str, data: dict[str, Any]):
        if not ObjectId.is_valid(product_id):
            return None
        data = dict(data)
        data["price"] = float(data["price"])
        document = self.collection.find_one_and_update(
            {"_id": ObjectId(product_id)},
            {"$set": data},
            return_document=ReturnDocument.AFTER,
        )
        return self._serialize(document)

    def delete(self, product_id: str):
        if not ObjectId.is_valid(product_id):
            return False
        result = self.collection.delete_one({"_id": ObjectId(product_id)})
        return result.deleted_count == 1

    def close(self):
        self.client.close()
