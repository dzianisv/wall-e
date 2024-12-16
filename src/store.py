import os
import pymongo
from typing import List, Dict, Any
from langchain.schema import BaseMessage, AIMessage, HumanMessage, SystemMessage

class MongoMemoryStore:
    def __init__(self, mongo_uri: str = "YOUR_MONGO_URI", db_name="langchain", collection_name="conversations"):
        self.client = pymongo.MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.collection = self.db[collection_name]

    def get_conversation(self, user_id: str) -> List[BaseMessage]:
        doc = self.collection.find_one({"user_id": user_id})
        if not doc or "messages" not in doc:
            return []
        # Convert stored dicts back to BaseMessage objects
        messages = []
        for m in doc["messages"]:
            if m["type"] == "human":
                messages.append(HumanMessage(content=m["content"]))
            elif m["type"] == "ai":
                messages.append(AIMessage(content=m["content"]))
            else:
                messages.append(SystemMessage(content=m["content"]))
        return messages

    def save_conversation(self, user_id: str, messages: List[BaseMessage]):
        # Convert BaseMessage objects to dicts for Mongo
        msg_dicts = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                msg_dicts.append({"type": "human", "content": msg.content})
            elif isinstance(msg, AIMessage):
                msg_dicts.append({"type": "ai", "content": msg.content})
            else:
                msg_dicts.append({"type": "system", "content": msg.content})

        self.collection.update_one({"user_id": user_id}, {"$set": {"messages": msg_dicts}}, upsert=True)
