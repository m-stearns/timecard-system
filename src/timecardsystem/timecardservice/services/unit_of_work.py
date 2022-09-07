import abc

import pymongo
from timecardsystem.timecardservice.adapters import repositories
from timecardsystem.timecardservice import config
from timecardsystem.timecardservice.adapters import odm


class AbstractUnitOfWork(abc.ABC):
    employees: repositories.AbstractEmployeeRepository
    timecards: repositories.AbstractTimecardRepository

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    def collect_new_events(self):
        if self.timecards.seen:
            for timecard in self.timecards.seen:
                while timecard.events:
                    yield timecard.events.pop(0)
        if self.employees.seen:
            for employee in self.employees.seen:
                while employee.events:
                    yield employee.events.pop(0)

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


def create_default_session() -> pymongo.database.Database:
    # starts up the client connection to the database
    # schema restrictions for all collections.
    client = pymongo.MongoClient(config.get_mongodb_uri())
    odm.startup_timecards_collection(client)
    return client.start_session


class MongoDBUnitOfWork(AbstractUnitOfWork):

    def __init__(self, session_factory=create_default_session) -> None:
        self.session_factory = session_factory

    def __enter__(self):
        self.session: pymongo.client_session.ClientSession = \
            self.session_factory()
        self.session.start_transaction()
        self.timecards = repositories.MongoDBTimecardRepository(
            self.session
        )
        self.employees = repositories.MongoDBEmployeeRepository(
            self.session
        )
        return super().__enter__()

    def _commit(self):
        self.session.commit_transaction()

    def rollback(self):
        # pymongo raises an error if a successfully committed transaction
        # is aborted; this is a workaround for the error.
        try:
            self.session.abort_transaction()
        except pymongo.errors.InvalidOperation:
            pass
