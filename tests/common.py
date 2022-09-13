from datetime import datetime
from decimal import Decimal
from typing import Dict

from timecardsystem.timecardservice.domain import model


def create_datetime_from_iso(date_ISO_format: str) -> datetime:
    return datetime.fromisoformat(date_ISO_format)


def create_dates_and_hours() -> Dict[str, Dict[str, str]]:
    return {
        create_datetime_from_iso("2022-08-08"): {
            "work_hours": "8.0",
            "sick_hours": "0.0",
            "vacation_hours": "0.0"
        },
        create_datetime_from_iso("2022-08-09"): {
            "work_hours": "8.0",
            "sick_hours": "0.0",
            "vacation_hours": "0.0"
        },
        create_datetime_from_iso("2022-08-10"): {
            "work_hours": "8.0",
            "sick_hours": "0.0",
            "vacation_hours": "0.0"
        },
        create_datetime_from_iso("2022-08-11"): {
            "work_hours": "8.0",
            "sick_hours": "0.0",
            "vacation_hours": "0.0"
        },
        create_datetime_from_iso("2022-08-12"): {
            "work_hours": "8.0",
            "sick_hours": "0.0",
            "vacation_hours": "0.0"
        },
    }


def convert_dates_and_hours_to_domain(
    dates_and_hours: Dict[datetime, Dict[str, str]]
) -> Dict[datetime, model.WorkDayHours]:
    model_dates_and_hours = {}
    for date, hours in dates_and_hours.items():
        model_dates_and_hours[date] = model.WorkDayHours(
            work_hours=Decimal(hours["work_hours"]),
            sick_hours=Decimal(hours["sick_hours"]),
            vacation_hours=Decimal(hours["vacation_hours"])
        )
    return model_dates_and_hours
