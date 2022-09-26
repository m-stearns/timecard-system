# Timecard System - An Event-Driven Microservice
## Description
The Timecard System allows users to create and save timecards for payment processing. Users can issue commands to create new Employee profiles and Timecards for each week they completed work. When Employee profiles and Timecards are created, or when a user indicates a Timecard is ready to be submitted for payment processing, the system issues Events to notify external services - such as Payroll payment service.

This application consumes commands and events which provide context to the creation and changes of entities and value objects within the application. Commands and Events are associated with their own domain services (in this case known as command and event handlers) which run the different business use cases for the application. The application also uses Command-Query Responsibility Segregration (CQRS) to allow separate scaling of the view (read) model from the data (update) model. An external publishing service (RabbitMQ) notifies other services when the application processes certain commands and events. All changes to entities are persisted in a MongoDB database.

## Technologies Used
1. Python
2. Flask (a web application framework)
3. Docker (for containerization of each service)
4. MongoDB (for persistence of data model and view model)
5. MongoDB Compass (a user friendly UI to administer MongoDB nodes)
5. RabbitMQ (for publishing external Events)
6. Pika (a python client used to interact with RabbitMQ)
7. Pytest (for unit testing, integration tests, and end-to-end tests)
8. Tenacity (used for retry attempts when verifying if services are available prior to running tests)
9. Makefile (broad commands to build, start, and teardown docker containers, as well as run tests within the containers)

## Challenges and Future Changes
### Challenges
1. The Community version of MongoDB does not provide an in-memory storage engine (whereas the [Enterprise version of MongoDB does provide one.](https://www.mongodb.com/docs/manual/core/inmemory/)). This forced the tests using the Timecard and Employee repositories to use a spun-up Docker instance hosting a MongoDB database, where I had to control the state of the database prior to and after running each individual test. Ultimately this means great care should be taken to manage the database in different testing environments - if the fixtures for these tests are hooked up to a test environment's database where the database is supposed to contain data within it and not be removed, the data will be wiped during test runs.
2. MongoDB does not provide transactions without a replica set or shards. Currently the project is setup to use a single MongoDB node for data persistence. As a result, persistence failures are not allowed to be rolled back like in a typical transaction. In the future I will change the project to use a replica set to allow the use of transaction features with MongoDB.
3. Pika's message consumers to receive messages from RabbitMQ by nature are blocking calls. However in order to test receiving messages to the MessageConsumerDTO we need to be able to tell the Consumer to gather messages for a period of time and then stop itself so we can run assertions against what messages were received. For this test we used a seperate thread to start the Consumer after durable events were published. As the Consumer runs it passes its binary messages to the MessageConsumerDTO which changes those binary messages back into domain events. Once an alloted set of time is passed, we stop the Consumer and request the thread to be joined back to the main thread running the test. From there we can inspect the received events and make sure we've received the correct events in the correct order. We also controlled the state of the RabbitMQ exchange and queue during tests by flushing the queue just prior to running each test.

### Future Changes
1. Making a replica set for the persistence database, to allow the use of transactions and rollbacks.
2. Adding the Payroll / Payment service, which will receive only submitted (not created) timecards from RabbitMQ and split their work day hours into appropriate Pay Periods. The user of this service would then choose a Pay Period to pay - for the work day hours that have been unpaid, this will flip their status to paid and also send an event to the Timecard service to indicate which work day hours are paid. The Timecard entity will then adjust its paid status to either Fully Paid or Partially Paid (such as when the dates within a timecard span 2 different pay periods). When the timecard entity receives PAID events for all of the work day hours within the timecard, the timecard will adjust its paid status to Fully Paid.
3. Implementing consumer entrypoints for both the Timecard service and Payroll / Payment service.

## Installation
### Prerequisites
You'll need the following services installed and running before you can run this app locally:
1. A working instance of a Linux-based operating system (this project was created using an instance of Ubuntu Linux 20.04 LTS)
2. [Docker, Docker Compose & Docker Desktop](https://docs.docker.com/get-docker/) for building Docker images, starting and stopping Docker containers, and running commands against services

### Local Development
To get started with local development, first clone the repository using
```
git clone https://github.com/m-stearns/timecard-system.git
```
and start-up [Docker Desktop](https://www.docker.com/products/docker-desktop/).

#### Starting up the application
1. Create the Docker images using a pre-defined Makefile command: `make build`
2. Start-up the Docker containers using a pre-defined Makefile command: `make up`

### How to Run Unit Tests, Integration Tests, and End-to-End Tests
Running tests against the application can be done either using [Docker](https://www.docker.com/) or a local [Python virtual environment](https://docs.python.org/3/library/venv.html).

#### Run Tests Using Docker
1. Run the tests using a pre-defined Makefile command: `make test`

#### Run Tests Using a Virtual Environment
1. Create a clean python virtual environment: `python3 -m venv venv`
2. Activate the virutal environment: `source venv/bin/activate`
3. Update `pip` in the virtual environment: `python3 -m pip install --upgrade pip`
4. Install the application requirements: `python3 -m pip install -r requirements.txt`
5. Inside the root directory, install the `src` package into your virtual environment (with editable mode turned on) with the following command: `python3 -m pip install -e ./src/`
6. Run the tests using the following command: `pytest`

## How to Use Timecard System
To use the timecard system, first follow the Local Development instructions shown above to start-up the application.

The application provides four available endpoints:
```
POST /employees                         # creates employee entity
POST /timecards                         # creates timecard entity (associated with employee)
POST /timecards/{timecard_id}/submit    # submit the timecard to be processed for payment
GET /employees/{employee_id}/timecards  # view all timecards for a specific employee
```

*Note: Each resource must be prefixed with the application URL: for local development use* `http://localhost:5005`

To create your first Employee, try running a `POST` request against `http://localhost:5005/employees` with the following JSON:

```
{
  "employee_id": "597f3b8f-f79a-446f-8b66-4777728674e6"
  "name": "Fred Warner"
}
```

Upon successful creation of the Employee resource, you should see a `201 Created` response.

### Domain Constraints
Employee entities must be created first before Timecard entities can be created and assigned to an Employee. When creating a new Timecard using `POST /timecards` you must supply the Employee's ID and Timecard ID both in UUID4 form.

The `week_ending_date` is an ISO format date (`YYYY-MM-DD`) which represents the date of the Friday in a typical timecard (Monday/Tuesday/Wednesday/Thursday/Friday).

`dates_and_hours` represents each date in the timecard (in ISO format - `YYYY-MM-DD`), with its corresponding `work_hours`, `sick_hours`, and `vacation_hours` per date, represented as strings of decimal-like values.

See below for an example of an HTTP `POST` request to `/timecards`:

```
{
  "timecard_id": "2437bf34-ef8a-4af2-8bd0-609d09cb4e5c",
  "employee_id": "597f3b8f-f79a-446f-8b66-4777728674e6",
  "week_ending_date": "2022-08-12",
  "dates_and_hours": {
    "2022-08-08": {
      "work_hours": "8.0",
      "sick_hours": "0.0",
      "vacation_hours": "0.0"
    },
    "2022-08-09": {
      "work_hours": "8.0",
      "sick_hours": "0.0",
      "vacation_hours": "0.0"
    },
    "2022-08-10": {
      "work_hours": "8.0",
      "sick_hours": "0.0",
      "vacation_hours": "0.0"
    },
    "2022-08-11": {
      "work_hours": "8.0",
      "sick_hours": "0.0",
      "vacation_hours": "0.0"
    },
    "2022-08-12": {
      "work_hours": "8.0",
      "sick_hours": "0.0",
      "vacation_hours": "0.0"
    }
  }
}
```

You can continue to alter the values of a specific timecard by continuing to make `POST` requests to `/timecards` with a specific Timecard ID in UUID4 format.

Finally when there are no more updates to a specific timecard, the timecard can be submitted for payment via `POST /timecards/{timecard_id}/submit` and providing the timecard's ID UUID4 value within a JSON body.

```
{
  "timecard_id": "2437bf34-ef8a-4af2-8bd0-609d09cb4e5c"
}
```

To view all timecards for a specific employee, use the `GET /employees/{employee_id}/timecards` endpoint by providing the Employee ID as a query parameter in UUID4 format. Upon a successful request a `200 OK` status will be returned along with a list of the employee's timecards in JSON format.

```
[
  {
    "employee_id": "597f3b8f-f79a-446f-8b66-4777728674e6",
    "employee_name": "Fred Warner",
    "timecard_id": "2437bf34-ef8a-4af2-8bd0-609d09cb4e5c",
    "week_ending_date": "2022-08-12",
    "dates_and_hours": {
      "2022-08-08": {
        "work_hours": "8.0",
        "sick_hours": "0.0",
        "vacation_hours": "0.0"
      },
      "2022-08-09": {
        "work_hours": "8.0",
        "sick_hours": "0.0",
        "vacation_hours": "0.0"
      },
      "2022-08-10": {
        "work_hours": "8.0",
        "sick_hours": "0.0",
        "vacation_hours": "0.0"
      },
      "2022-08-11": {
        "work_hours": "8.0",
        "sick_hours": "0.0",
        "vacation_hours": "0.0"
      },
      "2022-08-12": {
        "work_hours": "8.0",
        "sick_hours": "0.0",
        "vacation_hours": "0.0"
      }
    }
  }
]
```

### Employee Data Model
- `employee_id` (String / UUID4): The id of the Employee.
- `name` (String): The name of the Employee.

### Timecard Data Model
- `timecard_id` (String / UUID4): The id of the Timecard.
- `employee_id` (String / UUID4): The id of the Employee.
- `week_ending_date` (Date): The Friday of the timecard (the final day of a typical M-F 40 hour work week) in ISO format (YYYY-MM-DD).
- `dates_and_hours` (object): A map-like object - the keys are dates in ISO format (YYYY-MM-DD) and the value is another map-like object, where the keys are `work_hours`, `sick_hours`, and `vacation_hours`. There must be a minimum of 5 or more date keys provided in the `dates_and_hours` attribute. The value for each `*_hours` key is a decimal-like string representation of the number of hours, with only 1 decimal place. For example:
```
{    
  "dates_and_hours": {
    "2022-08-08": {
      "work_hours": "8.0",
      "sick_hours": "0.0",
       "vacation_hours": "0.0"
    },
    "2022-08-09": {
      "work_hours": "8.0",
      "sick_hours": "0.0",
      "vacation_hours": "0.0"
    },
    "2022-08-10": {
      "work_hours": "8.0",
      "sick_hours": "0.0",
      "vacation_hours": "0.0"
    },
    "2022-08-11": {
      "work_hours": "8.0",
      "sick_hours": "0.0",
      "vacation_hours": "0.0"
    },
    "2022-08-12": {
      "work_hours": "8.0",
      "sick_hours": "0.0",
      "vacation_hours": "0.0"
    }
  }
}
```
- `submitted` (bool): Indicates if the created timecard is also submitted by the user for payment processing.

## Credits
The architecture implementation for this project was inspired by [Architecture Patterns with Python](https://www.cosmicpython.com/) by Harry Percival and Bob Gregory. You can read this great book for free at [https://cosmicpython.com](https://www.cosmicpython.com/) thanks to the Creative Commons License CC-BY-NC-ND.

## License
This project is licensed under the GNU General Public License v3.0.