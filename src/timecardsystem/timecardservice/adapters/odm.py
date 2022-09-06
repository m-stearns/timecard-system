import pymongo
from collections import OrderedDict

DATABASE_NAME = "timecard-service"
COLLECTION_NAME = "Timecards"
TIMECARD_SCHEMA = {
    "timecard_id": {
        "type": "string",
        "required": True
    },
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


def create_timecards_validator():
    validator = {
        "$jsonSchema": {
            "bsonType": "object",
            "properties": {}
        }
    }
    required = []

    for field_name in TIMECARD_SCHEMA:
        field_properties = TIMECARD_SCHEMA[field_name]
        data_type = {"bsonType": field_properties["type"]}
        validator["$jsonSchema"]["properties"][field_name] = data_type

        if field_properties.get("required"):
            required.append(field_name)

    if len(required) > 0:
        validator["$jsonSchema"]["required"] = required

    return validator


def startup_timecards_collection(database: pymongo.database.Database):
    # create schema
    validator = create_timecards_validator()

    database.create_collection(COLLECTION_NAME)

    # add schema validation
    query = [('collMod', COLLECTION_NAME), ('validator', validator)]
    command_result = database.command(OrderedDict(query))

    # if our schema was rejected, fail everything
    if not command_result.get("ok", False):
        raise Exception
