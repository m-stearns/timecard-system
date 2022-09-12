from datetime import datetime
from decimal import Decimal
from typing import Dict, List
import pymongo
from timecardsystem.common.domain import model as common_model
from timecardsystem.timecardservice import config

DATABASE_NAME = "view_database"
EMPLOYEES_VIEW_COLLECTION_NAME = "view_employees"
TIMECARDS_VIEW_COLLECTION_NAME = "view_timecards"


def _connect_to_view_database():
    client = pymongo.MongoClient(config.get_mongodb_view_uri())
    view_db = client[DATABASE_NAME]
    return view_db


def _create_dates_and_hours_dto(
    dates_and_hours: Dict[datetime, List[Decimal]]
):
    dates_and_hours_dto = {}
    for date, hours in dates_and_hours.items():
        dates_and_hours_dto[date.isoformat()] = [
            str(hour) for hour in hours
        ]
    return dates_and_hours_dto


def add_employee_to_view_model(
    employee_id: common_model.EmployeeID,
    employee_name: common_model.EmployeeName
):
    view_db = _connect_to_view_database()
    employees_view_c = view_db[EMPLOYEES_VIEW_COLLECTION_NAME]
    row_data = {
        "_id": employee_id.value,
        "name": employee_name.value
    }
    employees_view_c.replace_one(
        filter={"_id": employee_id.value},
        replacement=row_data,
        upsert=True
    )


def add_timecard_to_view_model(
    employee_id: common_model.EmployeeID,
    employee_name: common_model.EmployeeName,
    timecard_id: common_model.TimecardID,
    week_ending_date: datetime,
    dates_and_hours: Dict[datetime, List[Decimal]]
):
    view_db = _connect_to_view_database()
    timecards_view_c = view_db[TIMECARDS_VIEW_COLLECTION_NAME]
    row_data = {
        "employee_id": employee_id.value,
        "employee_name": employee_name.value,
        "timecard_id": timecard_id.value,
        "week_ending_date": week_ending_date,
        "dates_and_hours": _create_dates_and_hours_dto(
            dates_and_hours
        )
    }
    timecards_view_c.replace_one(
        filter={"timecard_id": timecard_id.value},
        replacement=row_data,
        upsert=True
    )
