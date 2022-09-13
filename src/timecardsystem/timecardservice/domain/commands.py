from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from timecardsystem.common.domain import commands
from timecardsystem.common.domain import model as common_model
from timecardsystem.timecardservice.domain import model


@dataclass
class CreateEmployee(commands.Command):
    employee_id: str
    name: str


@dataclass
class CreateTimecard(commands.Command):
    timecard_id: common_model.TimecardID
    employee_id: common_model.EmployeeID
    week_ending_date: datetime
    dates_and_hours: Dict[datetime, model.WorkDayHours]


@dataclass
class SubmitTimecardForProcessing(commands.Command):
    timecard_id: common_model.TimecardID
