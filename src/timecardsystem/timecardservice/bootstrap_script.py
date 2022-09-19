from typing import Callable
from timecardsystem.timecardservice.adapters import rabbitmq_event_publisher
from timecardsystem.timecardservice.domain import commands, events
from timecardsystem.timecardservice.services import (handlers, message_bus,
                                                     unit_of_work)


class Bootstrap:

    def __init__(
        self,
        unit_of_work: unit_of_work.AbstractUnitOfWork =
        unit_of_work.MongoDBUnitOfWork(),
        collect_side_effect_events: bool = True,
        publish_external_events: bool = True,
        publisher: Callable = rabbitmq_event_publisher
    ):
        self.unit_of_work = unit_of_work
        self.initialized = False
        self.injected_command_handlers = {}
        self.injected_event_handlers = {}
        self.injected_external_event_handlers = {}
        self.collect_side_effect_events = collect_side_effect_events
        self.publish_external_events = publish_external_events
        self.publisher: rabbitmq_event_publisher = publisher

    def initialize_app(self):
        self.injected_command_handlers = {
            commands.CreateEmployee:
            lambda c: handlers.create_employee(c, self.unit_of_work),
            commands.CreateTimecard:
            lambda c: handlers.create_timecard(c, self.unit_of_work),
            commands.SubmitTimecardForProcessing:
            lambda c: handlers.submit_timecard_for_processing(
                c, self.unit_of_work
            ),
        }

        self.injected_event_handlers = {
            events.TimecardCreated: [
                lambda e: handlers.add_timecard_to_view_model(
                    e, self.unit_of_work
                )
            ],
            events.EmployeeCreated: [
                lambda e: handlers.add_employee_to_view_model(e),
            ],
        }

        self.injected_external_event_handlers = {
            events.EmployeeCreated: [
                lambda e: handlers.publish_employee_created_event(
                    event=e,
                    publish_action=self.publisher.publish_event
                ),
            ],
            events.TimecardCreated: [
                lambda e: handlers.publish_timecard_created_event(
                    event=e,
                    publish_action=self.publisher.publish_event
                )
            ]
        }

        self.initialized = True

    def get_message_bus(self) -> message_bus.MessageBus:
        if self.initialized:
            return message_bus.MessageBus(
                self.unit_of_work,
                self.injected_command_handlers,
                self.injected_event_handlers,
                self.injected_external_event_handlers,
                self.publish_external_events,
                self.collect_side_effect_events
            )
        else:
            raise Exception
