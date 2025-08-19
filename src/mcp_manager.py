import logging
from typing import List, Optional, Any

from pymongo import MongoClient

from config import Config

logger = logging.getLogger(__name__)


class MCPManager:
    """Manage MCP server connections for users."""

    def __init__(self, client: Optional[MongoClient] = None):
        self.client = client or MongoClient(Config.mongo_uri)
        self.collection = self.client["walle"]["mcp_servers"]

    def list_servers(self, user_id: str) -> List[dict]:
        return list(self.collection.find({"user_id": user_id}))

    def add_server(self, user_id: str, url: str, token: Optional[str] = None, name: Optional[str] = None) -> Any:
        doc = {"user_id": user_id, "url": url, "token": token, "name": name}
        result = self.collection.insert_one(doc)
        logger.info("Added MCP server %s for user %s", url, user_id)
        return result.inserted_id

    def delete_server(self, user_id: str, index: int) -> bool:
        servers = self.list_servers(user_id)
        if 0 <= index < len(servers):
            _id = servers[index]["_id"]
            self.collection.delete_one({"_id": _id})
            logger.info("Deleted MCP server index %d for user %s", index, user_id)
            return True
        logger.warning("Failed to delete MCP server index %d for user %s", index, user_id)
        return False
