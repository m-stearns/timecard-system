from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from timecardsystem.common.domain import commands


@dataclass
class CreateEmployee(commands.Command):
    employee_id: str
    name: str


@dataclass
class CreateTimecard(commands.Command):
    timecard_id: str
    employee_id: str
    week_ending_date: datetime
    dates_and_hours: Dict[datetime, Dict[str, str]]


@dataclass
class SubmitTimecardForProcessing(commands.Command):
    timecard_id: str
