from datetime import datetime
from typing import Set

from timecardsystem.common.domain import model as common_model
from timecardsystem.timecardservice.adapters import repositories
from timecardsystem.timecardservice.bootstrap_script import Bootstrap
from timecardsystem.timecardservice.domain import commands, model
from timecardsystem.timecardservice.services import unit_of_work


class FakeEmployeeRepository(repositories.AbstractEmployeeRepository):

    def __init__(self, employees):
        self._employees: Set[model.Employee] = set(employees)

    def _add(self, employee: model.Employee):
        self._employees.add(employee)

    def _get(self, employee_id: common_model.EmployeeID):
        for employee in self._employees:
            if employee.id.value == employee_id.value:
                return employee
        return None


class FakeTimecardRepository(repositories.AbstractTimecardRepository):

    def __init__(self, timecards):
        self._timecards = set(timecards)

    def _add(self, timecard: model.Timecard):
        self._timecards.add(timecard)

    def _get(self, timecard_id: common_model.TimecardID):
        for timecard in self._timecards:
            if timecard.id.value == timecard_id.value:
                return timecard
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
    bootstrap = Bootstrap(
        start_persistence=False,
        unit_of_work=FakeUnitOfWork()
    )
    bootstrap.initialize_app()
    return bootstrap

def create_dates_and_hours():
    return {
        "2022-08-08": [8.0, 0.0, 0.0, 0.0],
        "2022-08-09": [8.0, 0.0, 0.0, 0.0],
        "2022-08-10": [8.0, 0.0, 0.0, 0.0],
        "2022-08-11": [8.0, 0.0, 0.0, 0.0],
        "2022-08-12": [8.0, 0.0, 0.0, 0.0]
    }

def create_week_ending_date(date_ISO_format: str) -> datetime:
    return datetime.fromisoformat(date_ISO_format).date()

class TestCreateTimecard:
    def test_create_timecard(self):
        bootstrap = create_test_bootstrap()
        message_bus = bootstrap.get_message_bus()

        week_ending_date = create_week_ending_date("2022-08-26")
        dates_and_hours = create_dates_and_hours()

        command = commands.CreateTimecard(
            common_model.TimecardID("c5def653-5315-4a4d-b9dc-78beae7e3013"),
            common_model.EmployeeID("c8b5734f-e4b4-47c8-a326-f79c23e696de"),
            employee_name="Fake Employee",
            week_ending_date=week_ending_date,
            dates_and_hours=dates_and_hours

        )
        message_bus.handle(command)
        timecard = message_bus.unit_of_work.timecards.get(
            common_model.TimecardID("c5def653-5315-4a4d-b9dc-78beae7e3013")
        )
        assert timecard
        assert timecard.employee.id.value == "c8b5734f-e4b4-47c8-a326-f79c23e696de"
        assert timecard.employee.name == "Fake Employee"
        assert timecard.week_ending_date == week_ending_date
