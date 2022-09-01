import abc

from timecardsystem.timecardservice.adapters import repositories


class AbstractUnitOfWork(abc.ABC):
    employees: repositories.AbstractEmployeeRepository
    timecards: repositories.AbstractTimecardRepository

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class ImplementedUnitOfWork(AbstractUnitOfWork):

    def _commit(self):
        pass

    def rollback(self):
        pass
