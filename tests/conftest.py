import pathlib
import time

import pymongo
import pytest
import requests
import tenacity
from timecardsystem.timecardservice import config
from timecardsystem.timecardservice.adapters import mongodb_view, odm


@pytest.fixture
def mongodb_database():
    odm.DATABASE_NAME = "test"
    client = pymongo.MongoClient(config.get_mongodb_uri())
    test_database = wait_for_mongodb_to_start_up(
        client, odm.DATABASE_NAME
    )
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


@pytest.fixture
def mongodb_view_database():
    mongodb_view.DATABASE_NAME = "test_view"
    client = pymongo.MongoClient(config.get_mongodb_view_uri())
    test_view_database = wait_for_mongodb_to_start_up(
        client, mongodb_view.DATABASE_NAME
    )
    return test_view_database


@pytest.fixture
def mongodb_view_session_factory(mongodb_view_database):
    def get_session():
        client = mongodb_view_database.client
        return client.start_session
    yield get_session()
    client = mongodb_view_database.client
    client.drop_database(mongodb_view.DATABASE_NAME)


# Keep retrying to get the test database until we reach
# 10 seconds, then give up
@tenacity.retry(stop=tenacity.stop_after_delay(10))
def wait_for_mongodb_to_start_up(
    client: pymongo.MongoClient,
    database_name: str
):
    return client[database_name]


@tenacity.retry(stop=tenacity.stop_after_delay(10))
def wait_for_api_to_be_available():
    return requests.get(config.get_api_url())


@pytest.fixture
def restart_timecardservice_api():
    (pathlib.Path(__file__).parent /
        "../src/timecardsystem/timecardservice/entrypoints/flask_app.py").touch()
    time.sleep(0.5)
    wait_for_api_to_be_available()


@pytest.fixture
def setup_and_destroy_mongodb_data():
    data_client = pymongo.MongoClient(config.get_mongodb_uri())
    wait_for_mongodb_to_start_up(
        data_client, odm.DATABASE_NAME
    )

    view_client = pymongo.MongoClient(config.get_mongodb_view_uri())
    wait_for_mongodb_to_start_up(
        view_client, mongodb_view.DATABASE_NAME
    )
    yield
    data_client.drop_database(odm.DATABASE_NAME)
    view_client.drop_database(mongodb_view.DATABASE_NAME)
