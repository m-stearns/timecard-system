from datetime import datetime

from timecardsystem.common.domain import model as common_model
from timecardsystem.timecardservice.domain import model

today = datetime.today()

def test_validate_total_hours_for_timecard_valid_hours():
    timecard = model.Timecard(
        common_model.TimecardID("2437bf34-ef8a-4af2-8bd0-609d09cb4e5c"),
        today,
        {
            datetime(2022, 8, 8): [8.0, 0.0, 0.0, 0.0],
            datetime(2022, 8, 9): [8.0, 0.0, 0.0, 0.0],
            datetime(2022, 8, 10): [8.0, 0.0, 0.0, 0.0],
            datetime(2022, 8, 11): [8.0, 0.0, 0.0, 0.0],
            datetime(2022, 8, 12): [8.0, 0.0, 0.0, 0.0],
        }
    )
    assert timecard._validate_total_hours() == True

def test_validate_total_hours_for_timecard_invalid_hours():
    timecard = model.Timecard(
        common_model.TimecardID("2437bf34-ef8a-4af2-8bd0-609d09cb4e5c"),
        today,
        {
            datetime(2022, 8, 8): [8.0, 0.0, 0.0, 0.0],
            datetime(2022, 8, 9): [8.0, 0.0, 0.0, 0.0],
            datetime(2022, 8, 10): [8.0, 0.0, 0.0, 0.0],
            datetime(2022, 8, 11): [0.0, 0.0, 0.0, 0.0],
            datetime(2022, 8, 12): [5.0, 0.0, 0.0, 0.0],
        }
    )
    assert timecard._validate_total_hours() == False

def test_validate_number_of_days_entered_valid():
    timecard = model.Timecard(
        common_model.TimecardID("2437bf34-ef8a-4af2-8bd0-609d09cb4e5c"),
        today,
        {
            datetime(2022, 8, 8): [8.0, 0.0, 0.0, 0.0],
            datetime(2022, 8, 9): [8.0, 0.0, 0.0, 0.0],
            datetime(2022, 8, 10): [8.0, 0.0, 0.0, 0.0],
            datetime(2022, 8, 11): [8.0, 0.0, 0.0, 0.0],
            datetime(2022, 8, 12): [8.0, 0.0, 0.0, 0.0],
        }
    )
    assert timecard._validate_number_of_days_entered() == True

def test_validate_number_of_days_entered_invalid():
    timecard = model.Timecard(
        common_model.TimecardID("2437bf34-ef8a-4af2-8bd0-609d09cb4e5c"),
        today,
        {
            datetime(2022, 8, 8): [8.0, 0.0, 0.0, 0.0],
            datetime(2022, 8, 9): [8.0, 0.0, 0.0, 0.0],
            datetime(2022, 8, 10): [8.0, 0.0, 0.0, 0.0],
            datetime(2022, 8, 11): [8.0, 0.0, 0.0, 0.0],
            datetime(2022, 8, 12): [8.0, 0.0, 0.0, 0.0],
            datetime(2022, 8, 13): [8.0, 0.0, 0.0, 0.0],
            datetime(2022, 8, 14): [8.0, 0.0, 0.0, 0.0],
            datetime(2022, 8, 15): [8.0, 0.0, 0.0, 0.0],
        }
    )
    assert timecard._validate_number_of_days_entered() == False