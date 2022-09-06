import abc
from datetime import datetime
from typing import Dict
from decimal import Decimal

import pymongo
from timecardsystem.common.domain import model as common_model
from timecardsystem.timecardservice.domain import model


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

    def add(self, timecard: model.Timecard):
        self._add(timecard)

    def get(self, timecard_id: common_model.TimecardID) -> model.Timecard:
        timecard = self._get(timecard_id)
        return timecard

    @abc.abstractmethod
    def _add(self, timecard: model.Timecard):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, timecard_id: common_model.TimecardID):
        raise NotImplementedError


class AbstractEmployeeRepository(AbstractRepository):

    def add(self, employee: model.Employee):
        self._add(employee)

    def get(self, employee_id: common_model.EmployeeID) -> model.Employee:
        employee = self._get(employee_id)
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
        timecards_collection: pymongo.collection.Collection
    ) -> None:
        self.timecards_collection = timecards_collection

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
