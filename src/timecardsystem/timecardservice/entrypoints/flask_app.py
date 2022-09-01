from datetime import datetime

from flask import Flask, request
from timecardsystem.common.domain import model as common_model
from timecardsystem.timecardservice.domain import commands
from timecardsystem.timecardservice.bootstrap_script import Bootstrap

app = Flask(__name__)


@app.route("/timecards", methods=["GET", "POST"])
def create_timecard():
    timecard_id = request.json["timecard_id"]
    employee_id = request.json["employee_id"]
    employee_name = request.json["name"]
    week_ending_date = request.json["week_ending_date"]
    week_ending_date = datetime.fromisoformat(week_ending_date).date()

    dates_and_hours_dto = request.json["dates_and_hours"]
    dates_and_hours = {}
    for date_str, hours in dates_and_hours_dto.items():
        date = datetime.fromisoformat(date_str).date()
        dates_and_hours[date] = hours

    command = commands.TimecardCreated(
        common_model.TimecardID(timecard_id),
        common_model.EmployeeID(employee_id),
        employee_name,
        week_ending_date,
        dates_and_hours
    )

    bootstrap_script = Bootstrap()
    bootstrap_script.initialize_app()
    bus = bootstrap_script.get_message_bus()
    bus.handle(command)

    return "OK", 201
