import pymongo
import pytest
import tenacity

from timecardsystem.timecardservice import config
from timecardsystem.timecardservice.adapters import odm


@pytest.fixture
def mongodb_database():
    client = pymongo.MongoClient(config.get_mongodb_uri())
    test_database = wait_for_mongodb_to_start_up(client)
    return test_database


@pytest.fixture
def timecards_collection(mongodb_database):
    odm.startup_timecards_collection(mongodb_database)
    collection = mongodb_database[odm.COLLECTION_NAME]
    yield collection
    collection.drop()


# Keep retrying to get the test database until we reach
# 10 seconds, then give up
@tenacity.retry(stop=tenacity.stop_after_delay(10))
def wait_for_mongodb_to_start_up(client: pymongo.MongoClient):
    return client["test"]
