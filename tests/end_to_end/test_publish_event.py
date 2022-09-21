import json
import logging
import time
from threading import Thread

import pytest
import requests

from timecardsystem.common.dtos.message_dto import MessageConsumerDTO
from timecardsystem.timecardservice import config
from timecardsystem.timecardservice.entrypoints import rabbitmq_event_consumer

logging.disable(logging.CRITICAL)


@pytest.mark.usefixtures("restart_timecardservice_api")
def test_create_employee_command_sends_employee_created_event(
    setup_and_destroy_mongodb_data,
    start_up_rabbitmq,
    purge_rabbitmq_queue
):
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

    dto = MessageConsumerDTO()
    dto.set_deserializer(callable_func=json.loads)

    consumer = rabbitmq_event_consumer.Consumer()
    consumer.set_on_message_callback(dto.receive_message)

    t = Thread(target=consumer.start)
    t.start()
    time.sleep(5)
    consumer.stop()
    t.join()

    assert len(dto.deserialized_messages) > 0

    event = dto.deserialized_messages.pop(0)
    assert event.employee_id.value == employee_id
    assert event.name.value == employee_name
    assert len(dto.deserialized_messages) == 0


@pytest.mark.usefixtures("restart_timecardservice_api")
def test_create_timecard_command_sends_timecard_created_event(
    setup_and_destroy_mongodb_data,
    start_up_rabbitmq,
    purge_rabbitmq_queue
):
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

    dto = MessageConsumerDTO()
    dto.set_deserializer(callable_func=json.loads)

    consumer = rabbitmq_event_consumer.Consumer()
    consumer.set_on_message_callback(dto.receive_message)

    t = Thread(target=consumer.start)
    t.start()
    time.sleep(5)
    consumer.stop()
    t.join()

    assert len(dto.deserialized_messages) == 2

    employee_created_event = dto.deserialized_messages.pop(0)
    assert employee_created_event.employee_id.value == employee_id
    assert employee_created_event.name.value == employee_name

    assert len(dto.deserialized_messages) == 1

    timecard_created_event = dto.deserialized_messages.pop(0)
    assert timecard_created_event.timecard_id.value == timecard_id
    assert timecard_created_event.employee_id.value == employee_id
    assert len(dto.deserialized_messages) == 0


@pytest.mark.usefixtures("restart_timecardservice_api")
def test_submit_timecard_command_creates_timecard_submitted_event(
    setup_and_destroy_mongodb_data,
    start_up_rabbitmq,
    purge_rabbitmq_queue
):
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

    payload = {
        "timecard_id": timecard_id
    }

    response = requests.post(
        f"{api_url}/timecards/submit", json=payload
    )
    assert response.status_code == 200

    dto = MessageConsumerDTO()
    dto.set_deserializer(callable_func=json.loads)

    consumer = rabbitmq_event_consumer.Consumer()
    consumer.set_on_message_callback(dto.receive_message)

    t = Thread(target=consumer.start)
    t.start()
    time.sleep(15)
    consumer.stop()
    t.join()

    assert len(dto.deserialized_messages) == 3

    employee_created_event = dto.deserialized_messages.pop(0)
    assert employee_created_event.employee_id.value == employee_id
    assert employee_created_event.name.value == employee_name

    assert len(dto.deserialized_messages) == 2

    timecard_created_event = dto.deserialized_messages.pop(0)
    assert timecard_created_event.timecard_id.value == timecard_id
    assert timecard_created_event.employee_id.value == employee_id

    assert len(dto.deserialized_messages) == 1

    timecard_submitted_event = dto.deserialized_messages.pop(0)
    assert timecard_submitted_event.timecard_id.value == timecard_id
    assert timecard_submitted_event.employee_id.value == employee_id

    assert len(dto.deserialized_messages) == 0
