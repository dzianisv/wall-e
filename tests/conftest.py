import pymongo
import pytest

@pytest.fixture(scope="session")
def mongo_client():
    try:
        client = pymongo.MongoClient("mongodb://localhost:27017", serverSelectionTimeoutMS=1000)
        client.admin.command("ping")
    except Exception:
        pytest.skip("mongod not running")
    yield client
    client.drop_database("walle")
    client.close()
