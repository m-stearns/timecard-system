from decimal import Decimal
from typing import Set

from timecardsystem.common.domain import model as common_model
from timecardsystem.timecardservice.adapters import repositories
from timecardsystem.timecardservice.bootstrap_script import Bootstrap
from timecardsystem.timecardservice.domain import commands, model
from timecardsystem.timecardservice.services import unit_of_work

from ..common import create_dates_and_hours, create_datetime_from_iso


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
        unit_of_work=FakeUnitOfWork(),
        handle_side_effect_events=False
    )
    bootstrap.initialize_app()
    return bootstrap


class TestCreateTimecard:
    def test_create_timecard(self):
        bootstrap = create_test_bootstrap()
        message_bus = bootstrap.get_message_bus()

        week_ending_date = create_datetime_from_iso("2022-08-26")
        dates_and_hours = create_dates_and_hours()

        command = commands.CreateTimecard(
            common_model.TimecardID("c5def653-5315-4a4d-b9dc-78beae7e3013"),
            common_model.EmployeeID("c8b5734f-e4b4-47c8-a326-f79c23e696de"),
            week_ending_date=week_ending_date,
            dates_and_hours=dates_and_hours

        )
        message_bus.handle(command)
        timecard = message_bus.unit_of_work.timecards.get(
            common_model.TimecardID("c5def653-5315-4a4d-b9dc-78beae7e3013")
        )
        assert timecard.id.value == "c5def653-5315-4a4d-b9dc-78beae7e3013"
        assert timecard.employee_id.value == \
            "c8b5734f-e4b4-47c8-a326-f79c23e696de"
        assert timecard.week_ending_date == week_ending_date
        assert timecard.dates_and_hours == dates_and_hours

    def test_existing_timecard(self):
        bootstrap = create_test_bootstrap()
        message_bus = bootstrap.get_message_bus()

        week_ending_date = create_datetime_from_iso("2022-08-26")
        dates_and_hours = create_dates_and_hours()

        command_1 = commands.CreateTimecard(
            common_model.TimecardID("c5def653-5315-4a4d-b9dc-78beae7e3013"),
            common_model.EmployeeID("c8b5734f-e4b4-47c8-a326-f79c23e696de"),
            week_ending_date=week_ending_date,
            dates_and_hours=dates_and_hours

        )
        message_bus.handle(command_1)

        changed_dates_and_hours = {
            create_datetime_from_iso("2022-08-08"): model.WorkDayHours(
                work_hours=Decimal("7.0"),
                sick_hours=Decimal("1.0"),
                vacation_hours=Decimal("0.0")
            ),
            create_datetime_from_iso("2022-08-10"): model.WorkDayHours(
                work_hours=Decimal("8.0"),
                sick_hours=Decimal("0.0"),
                vacation_hours=Decimal("0.0")
            ),
            create_datetime_from_iso("2022-08-11"): model.WorkDayHours(
                work_hours=Decimal("0.0"),
                sick_hours=Decimal("0.0"),
                vacation_hours=Decimal("8.0")
            ),
            create_datetime_from_iso("2022-08-12"): model.WorkDayHours(
                work_hours=Decimal("8.0"),
                sick_hours=Decimal("0.0"),
                vacation_hours=Decimal("0.0")
            ),
            create_datetime_from_iso("2022-08-13"): model.WorkDayHours(
                work_hours=Decimal("4.0"),
                sick_hours=Decimal("4.0"),
                vacation_hours=Decimal("0.0")
            ),
        }
        command_2 = commands.CreateTimecard(
            common_model.TimecardID("c5def653-5315-4a4d-b9dc-78beae7e3013"),
            common_model.EmployeeID("c8b5734f-e4b4-47c8-a326-f79c23e696de"),
            week_ending_date=week_ending_date,
            dates_and_hours=changed_dates_and_hours
        )
        message_bus.handle(command_2)

        timecard = message_bus.unit_of_work.timecards.get(
            common_model.TimecardID("c5def653-5315-4a4d-b9dc-78beae7e3013")
        )
        assert timecard.dates_and_hours == changed_dates_and_hours


class TestSubmitTimecardForProcessing:

    def test_submit_timecard_for_processing(self):
        bootstrap = create_test_bootstrap()
        message_bus = bootstrap.get_message_bus()

        week_ending_date = create_datetime_from_iso("2022-08-26")
        dates_and_hours = create_dates_and_hours()
        timecard_id = \
            common_model.TimecardID("c5def653-5315-4a4d-b9dc-78beae7e3013")

        command = commands.CreateTimecard(
            timecard_id,
            common_model.EmployeeID("c8b5734f-e4b4-47c8-a326-f79c23e696de"),
            week_ending_date=week_ending_date,
            dates_and_hours=dates_and_hours

        )
        message_bus.handle(command)

        command = commands.SubmitTimecardForProcessing(timecard_id)
        message_bus.handle(command)

        timecard = message_bus.unit_of_work.timecards.get(timecard_id)
        assert timecard.submitted is True


class TestCreateEmployee:

    def test_create_employee(self):
        bootstrap = create_test_bootstrap()
        message_bus = bootstrap.get_message_bus()

        employee_id = \
            common_model.EmployeeID("c8b5734f-e4b4-47c8-a326-f79c23e696de")
        command = commands.CreateEmployee(
            employee_id,
            common_model.EmployeeName("Azure Diamond")
        )
        message_bus.handle(command)
        employee = message_bus.unit_of_work.employees.get(employee_id)
        assert employee.id == employee_id
