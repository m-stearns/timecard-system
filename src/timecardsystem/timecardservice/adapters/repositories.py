import abc

from timecardsystem.common.domain import model as common_model
from timecardsystem.timecardservice.domain import model


class AbstractTimecardRepository(abc.ABC):

    def add(self, timecard: model.Timecard):
        self._add(timecard)

    def get(self, timecard_id: common_model.TimecardID) -> model.Timecard:
        timecard = self._get(timecard_id)
        return timecard

    @abc.abstractmethod
    def _add(self, timecard: model.Timecard):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, timecard_id: common_model.TimecardID):
        raise NotImplementedError


class AbstractEmployeeRepository(abc.ABC):

    def add(self, employee: model.Employee):
        self._add(employee)

    def get(self, employee_id: common_model.EmployeeID) -> model.Employee:
        employee = self._get(employee_id)
        return employee

    @abc.abstractmethod
    def _add(self, employee: model.Employee):
        raise NotImplementedError

    @abc.abstractmethod
    def _get(self, employee_id: common_model.EmployeeID):
        raise NotImplementedError
