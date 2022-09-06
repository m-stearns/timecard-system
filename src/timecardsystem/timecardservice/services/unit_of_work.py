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

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


def create_default_database() -> pymongo.database.Database:
    # starts up the database connection and sets any
    # schema restrictions for all collections.
    client = pymongo.MongoClient(config.get_mongodb_uri())
    database = client[odm.DATABASE_NAME]
    odm.startup_timecards_collection(database)
    return database


class MongoDBUnitOfWork(AbstractUnitOfWork):

    def __init__(self, database_factory=create_default_database) -> None:
        self.database_factory = database_factory

    def __enter__(self):
        self.database = self.database_factory()
        self.timecards = repositories.MongoDBTimecardRepository(
            self.database[odm.COLLECTION_NAME]
        )
        return super().__enter__()

    def _commit(self):
        pass

    def rollback(self):
        pass
