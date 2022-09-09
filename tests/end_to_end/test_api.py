import pytest
import requests
from timecardsystem.timecardservice import config
from timecardsystem.timecardservice.adapters import odm, mongodb_view


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
