from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from timecardsystem.common.domain import events
from timecardsystem.common.domain import model as common_model


@dataclass
class TimecardCreated(events.Event):
    timecard_id: common_model.TimecardID
    employee_id: common_model.EmployeeID
    week_ending_date: datetime
    dates_and_hours: Dict[datetime, List[Decimal]]
