from timecardsystem.common.domain import model as common_model
from timecardsystem.timecardservice.adapters import odm
from timecardsystem.timecardservice.domain import model
from timecardsystem.timecardservice.services import unit_of_work


def test_can_save_an_employee(mongodb_session_factory):
    employee_id = common_model.EmployeeID(
        "94687e57-7316-4b92-8e76-4ac5c5c07230"
    )
    employee_name = common_model.EmployeeName("Azure Diamond")
    employee = model.Employee(
        employee_id, employee_name
    )

    test_unit_of_work = unit_of_work.MongoDBUnitOfWork(mongodb_session_factory)
    with test_unit_of_work:
        test_unit_of_work.employees.add(employee)
        test_unit_of_work.commit()

    session = mongodb_session_factory()
    client = session.client
    database = client[odm.DATABASE_NAME]
    employees_collection = database[odm.EMPLOYEES_COLLECTION_NAME]
    rows = employees_collection.find({"_id": employee_id.value})
    doc = rows[0]
    assert doc["_id"] == employee_id.value
    assert doc["name"] == employee_name.value


def test_can_retrieve_an_employee(mongodb_session_factory):
    employee_id = common_model.EmployeeID(
        "94687e57-7316-4b92-8e76-4ac5c5c07230"
    )
    employee_name = common_model.EmployeeName("Azure Diamond")

    session = mongodb_session_factory()
    client = session.client
    database = client[odm.DATABASE_NAME]
    employees_collection = database[odm.EMPLOYEES_COLLECTION_NAME]
    employees_collection.insert_one({
        "_id": employee_id.value,
        "name": employee_name.value
    })

    test_unit_of_work = unit_of_work.MongoDBUnitOfWork(mongodb_session_factory)
    employee = None
    with test_unit_of_work:
        employee = test_unit_of_work.employees.get(employee_id)

    assert employee.id == employee_id
    assert employee.name == employee_name
