from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from timecardsystem.common.domain import events
from timecardsystem.common.domain import model as common_model
from timecardsystem.timecardservice.domain import events as domain_events

MAX_DAYS_IN_TIMECARD = 7
MINIMUM_HOURS_PER_WEEK = 40
MINIMUM_HOURS_PER_DAY = 8


@dataclass(frozen=True)
class WorkDayHours:
    work_hours: Decimal
    sick_hours: Decimal
    vacation_hours: Decimal

    def total_hours(self) -> Decimal:
        return self.work_hours + self.vacation_hours + self.sick_hours

    def validate_work_day(self) -> bool:
        return self.total_hours >= MINIMUM_HOURS_PER_DAY

    def get_as_list_of_decimals(self) -> List[Decimal]:
        return [self.work_hours, self.sick_hours, self.vacation_hours]


class Employee(common_model.AggregateRoot):

    def __init__(
        self,
        employee_id: common_model.EmployeeID,
        name: common_model.EmployeeName
    ):
        super().__init__(employee_id)
        self.name = name
        self.events: List[events.Event] = []

    def confirm_employee_created(self):
        employee_created_event = domain_events.EmployeeCreated(
            self.id,
            self.name
        )
        self.events.append(employee_created_event)


class Timecard(common_model.AggregateRoot):

    def __init__(
        self,
        timecard_id: common_model.TimecardID,
        employee_id: common_model.EmployeeID,
        week_ending_date: datetime,
        dates_and_hours: Dict[datetime, WorkDayHours],
        submitted: bool = False
    ):
        super().__init__(timecard_id)
        self.employee_id = employee_id
        self.week_ending_date = week_ending_date
        self._dates_and_hours = dates_and_hours
        self.total_hours_in_week: Decimal = sum([
            work_day_hours.total_hours()
            for work_day_hours in self._dates_and_hours.values()
        ])
        self.number_of_days_entered: int = len(dates_and_hours)
        self.submitted = submitted
        self.events: List[events.Event] = []

    def validate_timecard(self):
        if not self._validate_total_hours():
            raise Exception
        if not self._validate_number_of_days_entered():
            raise Exception

    def _validate_total_hours(self):
        return self.total_hours_in_week >= MINIMUM_HOURS_PER_WEEK

    def _validate_number_of_days_entered(self):
        return self.number_of_days_entered <= MAX_DAYS_IN_TIMECARD

    def confirm_timecard_created(self):
        timecard_created_event = domain_events.TimecardCreated(
            self.id,
            self.employee_id,
            self.week_ending_date,
            {date: hours.get_as_list_of_decimals()
                for date, hours in self._dates_and_hours.items()}
        )
        self.events.append(timecard_created_event)

    @property
    def dates_and_hours(self) -> Dict[datetime, WorkDayHours]:
        return self._dates_and_hours

    @dates_and_hours.setter
    def dates_and_hours(
        self,
        new_dates_and_hours: Dict[datetime, WorkDayHours]
    ):
        self._dates_and_hours = new_dates_and_hours
