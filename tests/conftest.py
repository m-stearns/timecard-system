import pymongo
import pytest
import tenacity

from timecardsystem.timecardservice import config
from timecardsystem.timecardservice.adapters import odm


@pytest.fixture
def mongodb_database():
    odm.DATABASE_NAME = "test"
    client = pymongo.MongoClient(config.get_mongodb_uri())
    test_database = wait_for_mongodb_to_start_up(client)
    return test_database


@pytest.fixture
def mongodb_session_factory(mongodb_database):
    def get_session():
        client = mongodb_database.client
        return client.start_session
    odm.startup_timecards_collection(mongodb_database.client)
    odm.startup_employees_collection(mongodb_database.client)
    yield get_session()
    client = mongodb_database.client
    client.drop_database(odm.DATABASE_NAME)


# Keep retrying to get the test database until we reach
# 10 seconds, then give up
@tenacity.retry(stop=tenacity.stop_after_delay(10))
def wait_for_mongodb_to_start_up(client: pymongo.MongoClient):
    return client[odm.DATABASE_NAME]
