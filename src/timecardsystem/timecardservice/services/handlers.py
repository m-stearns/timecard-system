from datetime import datetime
from decimal import Decimal
from typing import Callable, Dict

from timecardsystem.common.domain import model as common_model
from timecardsystem.timecardservice.adapters import mongodb_view
from timecardsystem.timecardservice.domain import commands, events, model

from . import unit_of_work


class InvalidTimecard(Exception):
    pass


class EmployeeDoesNotExist(Exception):
    pass


def convert_dates_and_hours(
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


def create_employee(
    command: commands.CreateEmployee,
    unit_of_work: unit_of_work.AbstractUnitOfWork
):
    with unit_of_work:
        employee = model.Employee(
            common_model.EmployeeID(command.employee_id),
            common_model.EmployeeName(command.name)
        )
        unit_of_work.employees.add(employee)
        employee.confirm_employee_created()
        unit_of_work.commit()


def create_timecard(
    command: commands.CreateTimecard,
    unit_of_work: unit_of_work.AbstractUnitOfWork
):
    with unit_of_work:
        employee = unit_of_work.employees.get(
            common_model.EmployeeID(command.employee_id)
        )
        if not employee:
            raise EmployeeDoesNotExist(
                f"Employee ID {command.employee_id} does not exist"
            )
        timecard = unit_of_work.timecards.get(
            common_model.TimecardID(command.timecard_id)
        )
        if timecard:
            timecard.dates_and_hours = convert_dates_and_hours(
                command.dates_and_hours
            )
        else:
            timecard = model.Timecard(
                common_model.TimecardID(command.timecard_id),
                employee_id=common_model.EmployeeID(command.employee_id),
                week_ending_date=command.week_ending_date,
                dates_and_hours=convert_dates_and_hours(
                    command.dates_and_hours
                )
            )
        if not timecard.validate_timecard():
            raise InvalidTimecard(f"Invalid timecard {timecard.id.value}")
        unit_of_work.timecards.add(timecard)
        timecard.confirm_timecard_created()
        unit_of_work.commit()


def submit_timecard_for_processing(
    command: commands.SubmitTimecardForProcessing,
    unit_of_work: unit_of_work.AbstractUnitOfWork
):
    with unit_of_work:
        timecard = unit_of_work.timecards.get(
            common_model.TimecardID(command.timecard_id)
        )
        if timecard:
            timecard.submitted = True
            unit_of_work.timecards.add(timecard)
            unit_of_work.commit()


def add_employee_to_view_model(event: events.EmployeeCreated):
    mongodb_view.add_employee_to_view_model(
        common_model.EmployeeID(event.employee_id),
        common_model.EmployeeName(event.name)
    )


def add_timecard_to_view_model(
    event: events.TimecardCreated,
    unit_of_work: unit_of_work.AbstractUnitOfWork
):
    with unit_of_work:
        employee = unit_of_work.employees.get(
            common_model.EmployeeID(event.employee_id)
        )
        if not employee:
            raise Exception
        timecard = unit_of_work.timecards.get(
            common_model.TimecardID(event.timecard_id)
        )

        mongodb_view.add_timecard_to_view_model(
            employee.id,
            employee.name,
            timecard.id,
            timecard.week_ending_date,
            timecard.dates_and_hours
        )


def publish_employee_created_event(
    event: events.EmployeeCreated,
    publish_action: Callable
):
    publish_action("employee_created", event)
