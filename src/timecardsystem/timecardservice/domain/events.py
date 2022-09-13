from dataclasses import dataclass
from datetime import datetime
from typing import Dict

from timecardsystem.common.domain import events


@dataclass
class EmployeeCreated(events.Event):
    employee_id: str
    name: str


@dataclass
class TimecardCreated(events.Event):
    timecard_id: str
    employee_id: str
    week_ending_date: datetime
    dates_and_hours: Dict[datetime, Dict[str, str]]
