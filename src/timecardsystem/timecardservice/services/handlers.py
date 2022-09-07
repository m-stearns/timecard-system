from timecardsystem.timecardservice.domain import commands, model

from . import unit_of_work


def create_employee(
    command: commands.CreateEmployee,
    unit_of_work: unit_of_work.AbstractUnitOfWork
):
    with unit_of_work:
        employee = model.Employee(
            command.employee_id,
            command.name
        )
        unit_of_work.employees.add(employee)
        employee.confirm_employee_created()
        unit_of_work.commit()


def create_timecard(
    command: commands.CreateTimecard,
    unit_of_work: unit_of_work.AbstractUnitOfWork
):
    with unit_of_work:
        timecard = unit_of_work.timecards.get(command.timecard_id)
        if timecard:
            timecard.dates_and_hours = command.dates_and_hours
        else:
            timecard = model.Timecard(
                command.timecard_id,
                employee_id=command.employee_id,
                week_ending_date=command.week_ending_date,
                dates_and_hours=command.dates_and_hours
            )
        timecard.validate_timecard()
        unit_of_work.timecards.add(timecard)
        timecard.confirm_timecard_created()
        unit_of_work.commit()


def submit_timecard_for_processing(
    command: commands.SubmitTimecardForProcessing,
    unit_of_work: unit_of_work.AbstractUnitOfWork
):
    with unit_of_work:
        timecard = unit_of_work.timecards.get(command.timecard_id)
        if timecard:
            timecard.submitted = True
            unit_of_work.timecards.add(timecard)
            unit_of_work.commit()
