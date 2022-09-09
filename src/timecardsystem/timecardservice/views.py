from typing import Dict, List
from timecardsystem.timecardservice.services import unit_of_work
from timecardsystem.timecardservice.adapters import mongodb_view


def timecards_for_employee(
    employee_id: str,
    unit_of_work: unit_of_work.MongoDBViewUnitOfWork
) -> List[Dict[str, str]]:
    cursor = []
    with unit_of_work:
        client = unit_of_work.session.client
        view_database = client[mongodb_view.DATABASE_NAME]
        timecards_view_c = view_database[
            mongodb_view.TIMECARDS_VIEW_COLLECTION_NAME
        ]
        cursor = timecards_view_c.find({
            "employee_id": employee_id
        })
        return [doc for doc in cursor]
