import pytest
import requests
from timecardsystem.timecardservice import config


@pytest.mark.usefixtures("restart_timecardservice_api")
def test_post_to_create_employee(setup_and_destroy_mongodb_data):
    api_url = config.get_api_url()
    employee_id = "5dbf600d-305a-4f77-b2b8-51401f443597"
    employee_name = "Azure Diamond"
    payload = {
        "employee_id": employee_id,
        "name": employee_name
    }

    response = requests.post(
        f"{api_url}/employees", json=payload
    )
    assert response.status_code == 201


@pytest.mark.usefixtures("restart_timecardservice_api")
def test_post_to_create_timecard(setup_and_destroy_mongodb_data):
    api_url = config.get_api_url()
    employee_id = "5dbf600d-305a-4f77-b2b8-51401f443597"
    employee_name = "Azure Diamond"
    payload = {
        "employee_id": employee_id,
        "name": employee_name
    }

    response = requests.post(
        f"{api_url}/employees", json=payload
    )
    assert response.status_code == 201

    timecard_id = "aaa6eaa1-3197-4b3e-9b52-c91c55b91956"
    week_ending_date = "2022-08-12"
    dates_and_hours_json = {
        "2022-08-08": {
            "work_hours": "8.0",
            "sick_hours": "8.0",
            "vacation_hours": "8.0",
        },
        "2022-08-09": {
            "work_hours": "8.0",
            "sick_hours": "8.0",
            "vacation_hours": "8.0",
        },
        "2022-08-10": {
            "work_hours": "8.0",
            "sick_hours": "8.0",
            "vacation_hours": "8.0",
        },
        "2022-08-11": {
            "work_hours": "8.0",
            "sick_hours": "8.0",
            "vacation_hours": "8.0",
        },
        "2022-08-12": {
            "work_hours": "8.0",
            "sick_hours": "8.0",
            "vacation_hours": "8.0",
        },
    }

    payload = {
        "timecard_id": timecard_id,
        "employee_id": employee_id,
        "week_ending_date": week_ending_date,
        "dates_and_hours": dates_and_hours_json
    }

    response = requests.post(
        f"{api_url}/timecards", json=payload
    )
    assert response.status_code == 201
