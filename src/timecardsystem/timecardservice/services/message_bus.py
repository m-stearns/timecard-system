from typing import Union

from timecardsystem.timecardservice.services import unit_of_work
from timecardsystem.common.domain import commands, events

Message = Union[commands.Command, events.Event]

class MessageBus:

    def __init__(self, unit_of_work: unit_of_work.AbstractUnitOfWork) -> None:
        self.unit_of_work = unit_of_work

    def handle(self, message: Message):
        pass
