from typing import Dict
import pymongo
from collections import OrderedDict

DATABASE_NAME = "timecard-service"
TIMECARDS_COLLECTION_NAME = "timecards"
EMPLOYEES_COLLECTION_NAME = "employees"

TIMECARD_SCHEMA = {
    "employee_id": {
        "type": "string",
        "required": True
    },
    "week_ending_date": {
        "type": "date",
        "required": True
    },
    "dates_and_hours": {
        "type": "object",
        "required": True
    },
    "submitted": {
        "type": "bool",
        "required": True
    },
}

EMPLOYEE_SCHEMA = {
    "name": {
        "type": "string",
        "required": True
    }
}


def create_validator(schema: Dict[str, str]):
    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "properties": {}
        }
    }
    required = []

    for field_name in schema:
        field_properties = schema[field_name]
        data_type = {"bsonType": field_properties["type"]}
        validator["$jsonSchema"]["properties"][field_name] = data_type

        if field_properties.get("required"):
            required.append(field_name)

    if len(required) > 0:
        validator["$jsonSchema"]["required"] = required

    return validator


def startup_timecards_collection(client):
    database = client[DATABASE_NAME]
    # create schema
    validator = create_validator(TIMECARD_SCHEMA)

    try:
        database.create_collection(TIMECARDS_COLLECTION_NAME)
    except pymongo.errors.CollectionInvalid:
        pass

    # add schema validation
    query = [('collMod', TIMECARDS_COLLECTION_NAME), ('validator', validator)]
    command_result = database.command(OrderedDict(query))

    # if our schema was rejected, fail everything
    if not command_result.get("ok", False):
        raise Exception


def startup_employees_collection(client):
    database = client[DATABASE_NAME]
    # create schema
    validator = create_validator(EMPLOYEE_SCHEMA)

    try:
        database.create_collection(EMPLOYEES_COLLECTION_NAME)
    except pymongo.errors.CollectionInvalid:
        pass

    # add schema validation
    query = [('collMod', EMPLOYEES_COLLECTION_NAME), ('validator', validator)]
    command_result = database.command(OrderedDict(query))

    # if our schema was rejected, fail everything
    if not command_result.get("ok", False):
        raise Exception
