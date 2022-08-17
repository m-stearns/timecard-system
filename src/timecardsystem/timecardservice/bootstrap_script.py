from timecardsystem.timecardservice.services import message_bus, unit_of_work


class Bootstrap:

    def __init__(
        self,
        start_persistence: bool = True,
        unit_of_work: unit_of_work.AbstractUnitOfWork = unit_of_work.ImplementedUnitOfWork()
    ):
        self.start_persistence = start_persistence
        self.unit_of_work = unit_of_work
        self.initialized = False

    def initialize_app(self):
        if self.start_persistence:
            # start persistence mechanism here
            pass

        dependencies = {"unit_of_work": self.unit_of_work}
        self.initialized = True

    def get_message_bus(self):
        if self.initialized:
            return message_bus.MessageBus(
                self.unit_of_work
            )
        else:
            raise Exception

