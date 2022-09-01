from typing import Callable, Dict, Type, Union

from timecardsystem.common.domain import commands, events
from timecardsystem.timecardservice.services import unit_of_work

Message = Union[commands.Command, events.Event]


class MessageBus:

    def __init__(
        self,
        unit_of_work: unit_of_work.AbstractUnitOfWork,
        command_handlers: Dict[Type[commands.Command], Callable]
    ) -> None:
        self.unit_of_work = unit_of_work
        self.command_handlers = command_handlers
        self.queue = []

    def handle(self, message: Message):
        self.queue.append(message)
        while self.queue:
            message = self.queue.pop(0)
            if isinstance(message, commands.Command):
                self.handle_command(message)
            else:
                raise Exception(f"{message} is not a command!")

    def handle_command(self, command: commands.Command):
        handler = self.command_handlers[type(command)]
        handler(command)
