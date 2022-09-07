from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List

from timecardsystem.common.domain import commands
from timecardsystem.common.domain import model as common_model


@dataclass
class CreateTimecard(commands.Command):
    timecard_id: common_model.TimecardID
    employee_id: common_model.EmployeeID
    week_ending_date: datetime
    dates_and_hours: Dict[datetime, List[int]]

@dataclass
class SubmitTimecardForProcessing(commands.Command):
    timecard_id: common_model.TimecardID