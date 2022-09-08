from timecardsystem.timecardservice.domain import commands, events
from timecardsystem.timecardservice.services import (handlers, message_bus,
                                                     unit_of_work)


class Bootstrap:

    def __init__(
        self,
        unit_of_work: unit_of_work.AbstractUnitOfWork =
        unit_of_work.MongoDBUnitOfWork(),
        handle_side_effect_events: bool = True
    ):
        self.unit_of_work = unit_of_work
        self.initialized = False
        self.injected_command_handlers = {}
        self.injected_event_handlers = {}
        self.handle_side_effect_events = handle_side_effect_events

    def initialize_app(self):
        self.injected_command_handlers = {
            commands.CreateEmployee:
            lambda c: handlers.create_employee(c, self.unit_of_work),
            commands.CreateTimecard:
            lambda c: handlers.create_timecard(c, self.unit_of_work),
            commands.SubmitTimecardForProcessing:
            lambda c: handlers.submit_timecard_for_processing(
                c, self.unit_of_work
            )
        }
        self.injected_event_handlers = {
            events.TimecardCreated:
            lambda e: handlers.add_timecard_to_view_model(
                e, self.unit_of_work
            ),
            events.EmployeeCreated:
            lambda e: handlers.add_employee_to_view_model(e)
        }
        self.initialized = True

    def get_message_bus(self):
        if self.initialized:
            return message_bus.MessageBus(
                self.unit_of_work,
                self.injected_command_handlers,
                self.injected_event_handlers,
                self.handle_side_effect_events
            )
        else:
            raise Exception
