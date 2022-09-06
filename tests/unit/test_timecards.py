from decimal import Decimal

from timecardsystem.common.domain import model as common_model
from timecardsystem.timecardservice.domain import model

import common

week_ending_date = common.create_datetime_from_iso("2022-08-12")


def test_validate_total_hours_for_timecard_valid_hours():
    timecard = model.Timecard(
        common_model.TimecardID("2437bf34-ef8a-4af2-8bd0-609d09cb4e5c"),
        common_model.EmployeeID("2142eb3a-2435-4ae0-a98b-7060c574f257"),
        week_ending_date,
        common.create_dates_and_hours()
    )
    assert timecard._validate_total_hours() is True


def test_validate_total_hours_for_timecard_invalid_hours():
    invalid_dates_and_hours = {
        common.create_datetime_from_iso("2022-08-08"): model.WorkDayHours(
            work_hours=Decimal("7.0"),
            sick_hours=Decimal("0.0"),
            vacation_hours=Decimal("0.0")
        ),
        common.create_datetime_from_iso("2022-08-10"): model.WorkDayHours(
            work_hours=Decimal("8.0"),
            sick_hours=Decimal("0.0"),
            vacation_hours=Decimal("0.0")
        ),
        common.create_datetime_from_iso("2022-08-11"): model.WorkDayHours(
            work_hours=Decimal("0.0"),
            sick_hours=Decimal("0.0"),
            vacation_hours=Decimal("8.0")
        ),
        common.create_datetime_from_iso("2022-08-12"): model.WorkDayHours(
            work_hours=Decimal("8.0"),
            sick_hours=Decimal("0.0"),
            vacation_hours=Decimal("0.0")
        ),
        common.create_datetime_from_iso("2022-08-13"): model.WorkDayHours(
            work_hours=Decimal("0.0"),
            sick_hours=Decimal("4.0"),
            vacation_hours=Decimal("0.0")
        ),
    }

    timecard = model.Timecard(
        common_model.TimecardID("2437bf34-ef8a-4af2-8bd0-609d09cb4e5c"),
        common_model.EmployeeID("2142eb3a-2435-4ae0-a98b-7060c574f257"),
        week_ending_date,
        invalid_dates_and_hours
    )
    assert timecard._validate_total_hours() is False


def test_validate_number_of_days_entered_valid():
    timecard = model.Timecard(
        common_model.TimecardID("2437bf34-ef8a-4af2-8bd0-609d09cb4e5c"),
        common_model.EmployeeID("2142eb3a-2435-4ae0-a98b-7060c574f257"),
        week_ending_date,
        common.create_dates_and_hours()
    )
    assert timecard._validate_number_of_days_entered() is True


def test_validate_number_of_days_entered_invalid():
    dates_and_hours = common.create_dates_and_hours()

    dates_and_hours[common.create_datetime_from_iso("2022-08-13")] = \
        model.WorkDayHours(Decimal("8.0"), Decimal("0.0"), Decimal("0.0"))
    dates_and_hours[common.create_datetime_from_iso("2022-08-14")] = \
        model.WorkDayHours(Decimal("8.0"), Decimal("0.0"), Decimal("0.0"))
    dates_and_hours[common.create_datetime_from_iso("2022-08-15")] = \
        model.WorkDayHours(Decimal("8.0"), Decimal("0.0"), Decimal("0.0"))

    timecard = model.Timecard(
        common_model.TimecardID("2437bf34-ef8a-4af2-8bd0-609d09cb4e5c"),
        common_model.EmployeeID("2142eb3a-2435-4ae0-a98b-7060c574f257"),
        week_ending_date,
        dates_and_hours
    )
    assert timecard._validate_number_of_days_entered() is False
