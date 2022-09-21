from dataclasses import asdict
from datetime import datetime
from decimal import Decimal
from typing import Callable, Dict, List, Set

from pika.channel import Channel
from pika.spec import BasicProperties
from timecardsystem.common.domain import events as common_events
from timecardsystem.common.domain import model as common_model
from timecardsystem.timecardservice.domain import events, model


def convert_dates_and_hours_to_domain(
    dates_and_hours: Dict[str, Dict[str, str]]
) -> Dict[datetime, model.WorkDayHours]:
    model_dates_and_hours = {}
    for date, hours in dates_and_hours.items():
        model_dates_and_hours[datetime.fromisoformat(date)] = \
            model.WorkDayHours(
                work_hours=Decimal(hours["work_hours"]),
                sick_hours=Decimal(hours["sick_hours"]),
                vacation_hours=Decimal(hours["vacation_hours"])
            )
    return model_dates_and_hours


def create_dates_and_hours_dto(
    dates_and_hours: Dict[datetime, Dict[str, str]]
) -> Dict[str, str]:
    dates_and_hours_dto = {}
    for date, hours in dates_and_hours.items():
        dates_and_hours_dto[date.isoformat()] = {
            "work_hours": hours["work_hours"],
            "sick_hours": hours["sick_hours"],
            "vacation_hours": hours["vacation_hours"],
        }
    return dates_and_hours_dto


class MessagePublisherDTO:

    def __init__(self) -> None:
        self._serialized_message: bytes = None
        self._message_properties: str = None
        self._serialize_func: Callable = None

    def set_serializer(self, callable_func: Callable):
        self._serialize_func = callable_func

    def serialize_outgoing_message(self, message: common_events.Event):
        self._message_properties = message.__class__.__name__

        if message.__class__.__name__ == "EmployeeCreated":
            self._serialized_message = self._serialize_func(asdict(message))
        elif message.__class__.__name__ == "TimecardCreated":
            temp = asdict(message)
            temp["week_ending_date"] = temp["week_ending_date"].isoformat()
            temp["dates_and_hours"] = create_dates_and_hours_dto(
                temp["dates_and_hours"]
            )
            self._serialized_message = self._serialize_func(temp)
        elif message.__class__.__name__ == "TimecardSubmittedForProcessing":
            temp = asdict(message)
            self._serialized_message = self._serialize_func(temp)

    @property
    def serialized_message(self) -> bytes:
        return self._serialized_message

    @property
    def message_properties(self) -> str:
        return self._message_properties


class MessageConsumerDTO:

    def __init__(self) -> None:
        self._whitelisted_events: Set = \
            set({
                "EmployeeCreated",
                "TimecardCreated",
                "TimecardSubmittedForProcessing"
            })
        self._deserialize_func: Callable = None
        self._deserialized_messages: List[common_events.Event] = []
        self._app_callback: Callable = None

    def set_deserializer(self, callable_func: Callable):
        self._deserialize_func = callable_func

    def receive_message(
        self,
        channel: Channel,
        method,
        header: BasicProperties,
        body: bytes
    ) -> bool:
        """
        :param pika.channel.Channel channel
        :param pika.spec.Basic.Deliver method
        :param pika.spec.BasicProperties header
        :param bytes body
        """
        if self._can_be_deserialized(header):
            self._deserialize_message(channel, method, header, body)
            return True
        else:
            return False

    def _can_be_deserialized(self, header: BasicProperties) -> bool:
        return header.content_type in self._whitelisted_events

    def _deserialize_message(
        self,
        channel: Channel,
        method,
        header: BasicProperties,
        body: bytes
    ):
        """
        :param pika.channel.Channel channel
        :param pika.spec.Basic.Deliver method
        :param pika.spec.BasicProperties header
        :param bytes body
        """
        temp = self._deserialize_func(body)
        if header.content_type == "EmployeeCreated":
            event = events.EmployeeCreated(
                common_model.EmployeeID(temp["employee_id"]),
                common_model.EmployeeName(temp["name"])
            )
            self._deserialized_messages.append(event)
        elif header.content_type == "TimecardCreated":
            event = events.TimecardCreated(
                common_model.TimecardID(temp["timecard_id"]),
                common_model.EmployeeID(temp["employee_id"]),
                datetime.fromisoformat(temp["week_ending_date"]),
                convert_dates_and_hours_to_domain(temp["dates_and_hours"])
            )
            self._deserialized_messages.append(event)
        elif header.content_type == "TimecardSubmittedForProcessing":
            event = events.TimecardSubmittedForProcessing(
                common_model.TimecardID(temp["timecard_id"]),
                common_model.EmployeeID(temp["employee_id"])
            )
            self._deserialized_messages.append(event)

    @property
    def deserialized_messages(self) -> List[common_events.Event]:
        return self._deserialized_messages
