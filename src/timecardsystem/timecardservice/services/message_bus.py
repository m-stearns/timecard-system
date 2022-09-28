from typing import Callable, Dict, Type, Union

from timecardsystem.common.domain import commands, events
from timecardsystem.timecardservice.services import unit_of_work

Message = Union[commands.Command, events.Event]

# Code modified from class MessageBus obtained from
# https://github.com/cosmicpython/code/blob/master/src/allocation/service_layer/messagebus.py


class MessageBus:

    def __init__(
        self,
        unit_of_work: unit_of_work.AbstractUnitOfWork,
        command_handlers: Dict[Type[commands.Command], Callable],
        event_handlers: Dict[Type[events.Event], Callable],
        external_event_handlers: Dict[Type[events.Event], Callable],
        publish_external_events: bool = True,
        collect_side_effect_events: bool = True
    ) -> None:
        self.unit_of_work = unit_of_work
        self.command_handlers = command_handlers
        self.event_handlers = event_handlers
        self.external_event_handlers = external_event_handlers
        self.queue = []
        self.publish_external_events = publish_external_events
        self.collect_side_effect_events = collect_side_effect_events

    def handle(self, message: Message):
        self.queue.append(message)
        while self.queue:
            message = self.queue.pop(0)
            if isinstance(message, commands.Command):
                self.handle_command(message)
            elif isinstance(message, events.Event):
                self.handle_event(message)
            else:
                raise Exception(f"{message} is not an Event or Command!")

    def handle_command(self, command: commands.Command):
        handler = self.command_handlers[type(command)]
        handler(command)
        if self.collect_side_effect_events:
            self.queue.extend(self.unit_of_work.collect_events())

    def handle_event(self, event: events.Event):
        if type(event) in self.event_handlers:
            for handler in self.event_handlers[type(event)]:
                handler(event)
                if self.collect_side_effect_events:
                    self.queue.extend(self.unit_of_work.collect_events())

        if type(event) in self.external_event_handlers \
                and self.publish_external_events:
            for handler in self.external_event_handlers[type(event)]:
                handler(event)
