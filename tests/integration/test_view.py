from datetime import datetime
from typing import Set

import pytest
from timecardsystem.common.domain import model as common_model
from timecardsystem.timecardservice import bootstrap_script
from timecardsystem.timecardservice.domain import commands, model
from timecardsystem.timecardservice.services import message_bus, unit_of_work
from timecardsystem.timecardservice.adapters import repositories, mongodb_view
from timecardsystem.timecardservice import views

from ..common import create_dates_and_hours


class FakeTimecardRepository(repositories.AbstractTimecardRepository):

    def __init__(self, timecards):
        self._timecards = set(timecards)
        super().__init__()

    def _add(self, timecard: model.Timecard):
        self._timecards.add(timecard)

    def _get(self, timecard_id: common_model.TimecardID):
        for timecard in self._timecards:
            if timecard.id.value == timecard_id.value:
                return timecard
        return None


class FakeEmployeeRepository(repositories.AbstractEmployeeRepository):

    def __init__(self, employees):
        self._employees: Set[model.Employee] = set(employees)
        super().__init__()

    def _add(self, employee: model.Employee):
        self._employees.add(employee)

    def _get(self, employee_id: common_model.EmployeeID):
        for employee in self._employees:
            if employee.id.value == employee_id.value:
                return employee
        return None


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):

    def __init__(self) -> None:
        self.employees = FakeEmployeeRepository([])
        self.timecards = FakeTimecardRepository([])
        self.processed_commit = False

    def _commit(self):
        self.processed_commit = True

    def rollback(self):
        pass


def create_test_bootstrap():
    bootstrap = bootstrap_script.Bootstrap(
        unit_of_work=FakeUnitOfWork(),
        publish_external_events=False
    )
    bootstrap.initialize_app()
    return bootstrap


@pytest.fixture
def mongodb_view_bus(mongodb_view_session_factory):
    bootstrapper = bootstrap_script.Bootstrap(
        unit_of_work=unit_of_work.MongoDBViewUnitOfWork(
            mongodb_view_session_factory
        ),
    )
    bootstrapper.initialize_app()
    yield bootstrapper.get_message_bus()


def test_timecard_view(
    mongodb_view_bus: message_bus.MessageBus
):
    mongodb_view.DATABASE_NAME = "test_view"
    test_bootstrap = create_test_bootstrap()
    test_message_bus = test_bootstrap.get_message_bus()

    timecard_id = \
        common_model.TimecardID("b7f35f7f-3f08-44b7-9d84-b0b28d7237ef")
    employee_id = \
        common_model.EmployeeID("88f67519-f5dc-4ba1-8dac-03e024ccd251")
    employee_name = common_model.EmployeeName("Azure Diamond")
    week_ending_date = datetime.fromisoformat("2022-08-26")
    dates_and_hours_dto = create_dates_and_hours()

    test_message_bus.unit_of_work.employees.add(
        model.Employee(employee_id, employee_name)
    )

    command = commands.CreateTimecard(
        timecard_id,
        employee_id,
        week_ending_date,
        dates_and_hours_dto
    )
    test_message_bus.handle(command)

    rows = views.timecards_for_employee(
        employee_id.value, mongodb_view_bus.unit_of_work
    )
    doc = rows[0]
    assert doc["employee_id"] == employee_id.value
    assert doc["employee_name"] == employee_name.value
    assert doc["timecard_id"] == timecard_id.value
    assert doc["week_ending_date"] == week_ending_date
    assert "2022-08-08T00:00:00" in doc["dates_and_hours"]
    assert "2022-08-09T00:00:00" in doc["dates_and_hours"]
    assert "2022-08-10T00:00:00" in doc["dates_and_hours"]
    assert "2022-08-11T00:00:00" in doc["dates_and_hours"]
    assert "2022-08-12T00:00:00" in doc["dates_and_hours"]
