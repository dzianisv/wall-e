import os
import sys

import pytest
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from config import Config
from mcp_manager import MCPManager


def test_add_list_delete(mongo_client):
    manager = MCPManager(client=mongo_client)
    user_id = "user1"
    url = "https://example.com/mcp"
    manager.add_server(user_id, url)
    servers = manager.list_servers(user_id)
    assert len(servers) == 1
    assert servers[0]["url"] == url
    assert manager.delete_server(user_id, 0)
    assert manager.list_servers(user_id) == []


def test_gmail_integration(mongo_client):
    token = os.environ.get("GMAIL_API_TOKEN")
    if not token:
        pytest.skip("GMAIL_API_TOKEN not provided")

    manager = MCPManager(client=mongo_client)
    user_id = "user1"
    manager.add_server(user_id, Config.gmail_mcp_url, token=token)

    servers = manager.list_servers(user_id)
    assert servers[0]["token"] == token

    resp = requests.get(
        "https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=1",
        headers={"Authorization": f"Bearer {token}"},
        timeout=10,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert "messages" in data
