from timecardsystem.timecardservice.domain import commands, model

from . import unit_of_work


def create_timecard(
    command: commands.TimecardCreated,
    unit_of_work: unit_of_work.AbstractUnitOfWork
):
    with unit_of_work:
        employee = unit_of_work.employees.get(
            employee_id=command.employee_id
        )
        if not employee:
            employee = model.Employee(
                command.employee_id, command.employee_name
            )
            unit_of_work.employees.add(employee)

        new_timecard = model.Timecard(
            command.id,
            employee=employee,
            week_ending_date=command.week_ending_date,
            dates_and_hours=command.dates_and_hours
        )
        unit_of_work.timecards.add(new_timecard)
        unit_of_work.commit()
