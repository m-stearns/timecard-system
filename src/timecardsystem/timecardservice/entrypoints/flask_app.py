from datetime import datetime
from typing import Dict, List

from flask import Flask, jsonify, request
from timecardsystem.timecardservice import views
from timecardsystem.timecardservice.bootstrap_script import Bootstrap
from timecardsystem.timecardservice.domain import commands
from timecardsystem.timecardservice.services import handlers

app = Flask(__name__)


def create_dates_and_hours(dates_and_hours: Dict[str, Dict[str, str]]):
    dates_and_hours_dto = {}
    for date_str, hours in dates_and_hours.items():
        date_obj = datetime.fromisoformat(date_str)
        dates_and_hours_dto[date_obj] = hours

    return dates_and_hours_dto


@app.route("/employees", methods=["GET", "POST"])
def create_employee():
    employee_id = request.json["employee_id"]
    employee_name = request.json["name"]

    command = commands.CreateEmployee(
        str(employee_id), str(employee_name)
    )

    bootstrapper = Bootstrap()
    bootstrapper.initialize_app()
    bus = bootstrapper.get_message_bus()
    bus.handle(command)

    return "OK", 201


@app.route("/timecards", methods=["POST"])
def create_timecard():
    timecard_id = request.json["timecard_id"]
    employee_id = request.json["employee_id"]
    week_ending_date = request.json["week_ending_date"]
    week_ending_date = datetime.fromisoformat(week_ending_date)

    dates_and_hours_dto = create_dates_and_hours(
        request.json["dates_and_hours"]
    )

    command = commands.CreateTimecard(
        timecard_id,
        employee_id,
        week_ending_date,
        dates_and_hours_dto
    )

    bootstrapper = Bootstrap()
    bootstrapper.initialize_app()
    bus = bootstrapper.get_message_bus()

    try:
        bus.handle(command)
    except (handlers.InvalidTimecard, handlers.EmployeeDoesNotExist) as err:
        return {"error": str(err)}, 400

    return "OK", 201


@app.route("/timecards/submit", methods=["POST"])
def submit_timecard_for_processing():
    timecard_id = request.json["timecard_id"]
    command = commands.SubmitTimecardForProcessing(
        timecard_id=timecard_id
    )

    bootstrapper = Bootstrap()
    bootstrapper.initialize_app()
    bus = bootstrapper.get_message_bus()
    bus.handle(command)

    return "OK", 200


@app.route("/employees/<employee_id>/timecards", methods=["GET"])
def get_timecards_for_employee(employee_id: str):
    results: List[Dict[str, str]] = views.timecards_for_employee(employee_id)
    if not results:
        return "not found", 404
    return jsonify(results), 200
