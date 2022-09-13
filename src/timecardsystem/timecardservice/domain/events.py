from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from timecardsystem.common.domain import events
from timecardsystem.common.domain import model as common_model


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
