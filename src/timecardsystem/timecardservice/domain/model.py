from datetime import datetime
from typing import Dict, List

from timecardsystem.common.domain import events
from timecardsystem.common.domain import model as common_model

MAX_DAYS_IN_TIMECARD = 7
MINIMUM_HOURS = 40


class Employee(common_model.BaseEntity):

    def __init__(
        self,
        employee_id: common_model.EmployeeID,
        name: common_model.EmployeeName
    ):
        super().__init__(employee_id)
        self.name = name
        self.events: List[events.Event] = []


class Timecard(common_model.AggregateRoot):

    def __init__(
        self,
        timecard_id: common_model.TimecardID,
        employee: Employee,
        week_ending_date: datetime,
        dates_and_hours: Dict[datetime, List[int]],
        version: int = 0
    ):
        super().__init__(timecard_id)
        self.employee = employee
        self.week_ending_date = week_ending_date
        self.dates_and_hours = dates_and_hours
        self.total_hours: int = sum([sum(hours) for hours in self.dates_and_hours.values()])
        self.number_of_days_entered: int = len(dates_and_hours)
        self.submitted: bool = False
        self.version = version

    def validate_timecard(self):
        if not self._validate_total_hours():
            raise Exception
        if not self._validate_number_of_days_entered():
            raise Exception

    def _validate_total_hours(self):
        return self.total_hours >= MINIMUM_HOURS

    def _validate_number_of_days_entered(self):
        return self.number_of_days_entered <= MAX_DAYS_IN_TIMECARD
