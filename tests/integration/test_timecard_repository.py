from timecardsystem.common.domain import model as common_model
from timecardsystem.timecardservice.adapters import repositories
from timecardsystem.timecardservice.domain import model

from ..common import (convert_dates_and_hours_to_domain,
                      create_dates_and_hours, create_datetime_from_iso)

week_ending_date = create_datetime_from_iso("2022-08-12")


def test_get_timecard_by_id(mongodb_session_factory):
    session = mongodb_session_factory()
    timecard_repository = \
        repositories.MongoDBTimecardRepository(session)

    timecard_id = common_model.TimecardID(
        "2437bf34-ef8a-4af2-8bd0-609d09cb4e5c"
    )
    timecard = model.Timecard(
        timecard_id,
        common_model.EmployeeID("2142eb3a-2435-4ae0-a98b-7060c574f257"),
        week_ending_date,
        convert_dates_and_hours_to_domain(create_dates_and_hours())
    )
    timecard_repository.add(timecard)
    timecard = timecard_repository.get(timecard_id)
    assert timecard_id == timecard.id


def test_get_employee_by_id(mongodb_session_factory):
    session = mongodb_session_factory()
    employee_repository = \
        repositories.MongoDBEmployeeRepository(session)

    employee_id = common_model.EmployeeID(
        "2142eb3a-2435-4ae0-a98b-7060c574f257"
    )
    employee = model.Employee(
        employee_id,
        common_model.EmployeeName("Azure Diamond")
    )
    employee_repository.add(employee)
    employee = employee_repository.get(employee_id)
    assert employee_id == employee.id
