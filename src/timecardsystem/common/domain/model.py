import uuid
from dataclasses import dataclass
from typing import TypeVar


@dataclass(frozen=True)
class TimecardID:
    value: uuid.UUID


@dataclass(frozen=True)
class EmployeeID:
    value: uuid.UUID


@dataclass(frozen=True)
class EmployeeName:
    name: str


# Entities
ID = TypeVar("ID")


class BaseEntity:

    def __init__(self, id: ID):
        self._id: ID = id

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, id: ID):
        self._id = id

    def __eq__(self, other):
        if not isinstance(other, BaseEntity):
            return False
        return other.id == self.id

    def __hash__(self) -> int:
        return hash(self.id)


class AggregateRoot(BaseEntity):

    def __init__(self, id: ID):
        super().__init__(id)
