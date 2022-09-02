from datetime import datetime
from decimal import Decimal
from typing import Dict

from timecardsystem.timecardservice.domain import model


def create_date_from_iso(date_ISO_format: str) -> datetime:
    return datetime.fromisoformat(date_ISO_format).date()

def create_dates_and_hours() -> Dict[datetime, model.WorkDayHours]:
    return {
        create_date_from_iso("2022-08-08"): model.WorkDayHours(
            work_hours=Decimal("8.0"),
            sick_hours=Decimal("0.0"),
            vacation_hours=Decimal("0.0")
        ),
        create_date_from_iso("2022-08-09"): model.WorkDayHours(
            work_hours=Decimal("8.0"),
            sick_hours=Decimal("0.0"),
            vacation_hours=Decimal("0.0")
        ),
        create_date_from_iso("2022-08-10"): model.WorkDayHours(
            work_hours=Decimal("8.0"),
            sick_hours=Decimal("0.0"),
            vacation_hours=Decimal("0.0")
        ),
        create_date_from_iso("2022-08-11"): model.WorkDayHours(
            work_hours=Decimal("8.0"),
            sick_hours=Decimal("0.0"),
            vacation_hours=Decimal("0.0")
        ),
        create_date_from_iso("2022-08-12"): model.WorkDayHours(
            work_hours=Decimal("8.0"),
            sick_hours=Decimal("0.0"),
            vacation_hours=Decimal("0.0")
        ),
    }
