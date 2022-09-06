from timecardsystem.timecardservice.domain import commands
from timecardsystem.timecardservice.services import (handlers, message_bus,
                                                     unit_of_work)


class Bootstrap:

    def __init__(
        self,
        unit_of_work: unit_of_work.AbstractUnitOfWork =
            unit_of_work.MongoDBUnitOfWork()
    ):
        self.unit_of_work = unit_of_work
        self.initialized = False
        self.injected_command_handlers = {}

    def initialize_app(self):
        self.injected_command_handlers = {
            commands.CreateTimecard:
            lambda c: handlers.create_timecard(c, self.unit_of_work)
        }
        self.initialized = True

    def get_message_bus(self):
        if self.initialized:
            return message_bus.MessageBus(
                self.unit_of_work,
                self.injected_command_handlers
            )
        else:
            raise Exception
