import abc
from datetime import datetime
from typing import Dict
from decimal import Decimal

import pymongo
from timecardsystem.common.domain import model as common_model
from timecardsystem.timecardservice.domain import model
from timecardsystem.timecardservice.adapters import odm


def create_dates_and_hours_dto(
    dates_and_hours: Dict[datetime, model.WorkDayHours]
):
    dates_and_hours_dto = {}
    for date, hours in dates_and_hours.items():
        dates_and_hours_dto[date.isoformat()] = [
            str(hours.work_hours),
            str(hours.sick_hours),
            str(hours.vacation_hours)
        ]
    return dates_and_hours_dto


class AbstractRepository(abc.ABC):

    @abc.abstractmethod
    def add(self, obj):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, obj_id):
        raise NotImplementedError


class AbstractTimecardRepository(AbstractRepository):

    def __init__(self) -> None:
        self.seen = set()

    def add(self, timecard: model.Timecard):
        self._add(timecard)
        self.seen.add(timecard)

    def get(self, timecard_id: common_model.TimecardID) -> model.Timecard:
        timecard = self._get(timecard_id)
        if timecard:
            self.seen.add(timecard)
        return timecard

    @abc.abstractmethod
    def _add(self, timecard: model.Timecard):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, timecard_id: common_model.TimecardID):
        raise NotImplementedError


class AbstractEmployeeRepository(AbstractRepository):

    def __init__(self) -> None:
        self.seen = set()

    def add(self, employee: model.Employee):
        self._add(employee)
        self.seen.add(employee)

    def get(self, employee_id: common_model.EmployeeID) -> model.Employee:
        employee = self._get(employee_id)
        if employee:
            self.seen.add(employee)
        return employee

    @abc.abstractmethod
    def _add(self, employee: model.Employee):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, employee_id: common_model.EmployeeID):
        raise NotImplementedError


class MongoDBTimecardRepository(AbstractTimecardRepository):

    def __init__(
        self,
        session: pymongo.client_session.ClientSession
    ) -> None:
        self.session = session
        self.database = session.client[odm.DATABASE_NAME]
        self.timecards_collection = \
            self.database[odm.TIMECARDS_COLLECTION_NAME]
        super().__init__()

    def _add(self, timecard: model.Timecard):
        dates_and_hours_dto = \
            create_dates_and_hours_dto(timecard.dates_and_hours)

        timecard_dto = {
            "_id": timecard.id.value,
            "employee_id": timecard.employee_id.value,
            "week_ending_date": timecard.week_ending_date,
            "dates_and_hours": dates_and_hours_dto,
            "submitted": timecard.submitted
        }
        self.timecards_collection.replace_one(
            filter={"_id": timecard.id.value},
            replacement=timecard_dto,
            upsert=True
        )

    def _get(self, timecard_id: common_model.TimecardID) -> model.Timecard:
        timecard_dto = \
            self.timecards_collection.find_one(
                {"_id": timecard_id.value}
            )
        if timecard_dto:
            dates_and_hours = {}
            for date, hours in timecard_dto["dates_and_hours"].items():
                date_obj = datetime.fromisoformat(date)
                work_day_hours = model.WorkDayHours(
                    work_hours=Decimal(hours[0]),
                    sick_hours=Decimal(hours[1]),
                    vacation_hours=Decimal(hours[2]),
                )
                dates_and_hours[date_obj] = work_day_hours

            timecard = model.Timecard(
                common_model.TimecardID(timecard_dto["_id"]),
                common_model.EmployeeID(timecard_dto["employee_id"]),
                timecard_dto["week_ending_date"],
                dates_and_hours,
                timecard_dto["submitted"]
            )
            return timecard
        else:
            return None


class MongoDBEmployeeRepository(AbstractEmployeeRepository):

    def __init__(
        self,
        session: pymongo.client_session.ClientSession
    ) -> None:
        self.session = session
        self.database = session.client[odm.DATABASE_NAME]
        self.employees_collection = \
            self.database[odm.EMPLOYEES_COLLECTION_NAME]
        super().__init__()

    def _add(self, employee: model.Employee):
        employee_dto = {
            "_id": employee.id.value,
            "name": employee.name.value
        }
        self.employees_collection.replace_one(
            filter={"_id": employee.id.value},
            replacement=employee_dto,
            upsert=True
        )

    def _get(self, employee_id: common_model.EmployeeID) -> model.Employee:
        employee_dto = \
            self.employees_collection.find_one(
                {"_id": employee_id.value}
            )
        if employee_dto:
            employee = model.Employee(
                common_model.EmployeeID(employee_dto["_id"]),
                common_model.EmployeeName(employee_dto["name"]),
            )
            return employee
        else:
            return None
