from timecardsystem.common.domain import model as common_model
from timecardsystem.timecardservice.services import unit_of_work
from timecardsystem.timecardservice.adapters import mongodb_view


def timecards_for_employee(
    employee_id: common_model.EmployeeID,
    unit_of_work: unit_of_work.MongoDBViewUnitOfWork
):
    cursor = []
    with unit_of_work:
        client = unit_of_work.session.client
        view_database = client[mongodb_view.DATABASE_NAME]
        timecards_view_c = view_database[
            mongodb_view.TIMECARDS_VIEW_COLLECTION_NAME
        ]
        cursor = timecards_view_c.find({
            "employee_id": employee_id.value
        })
        return [doc for doc in cursor]
