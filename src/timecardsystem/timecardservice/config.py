import os


def get_mongodb_uri() -> str:
    # configure the URI depending on if app is running
    # locally outside of containers OR within containers
    host = os.environ.get("DB_HOST", "localhost")
    port = 17017 if host == "localhost" else 27017
    password = os.environ.get("DB_PASSWORD", "hunter2")
    user_name = "AzureDiamond"
    return f"mongodb://{user_name}:{password}@{host}:{port}"


def get_mongodb_view_uri() -> str:
    host = os.environ.get("DB_VIEW_HOST", "localhost")
    port = 17018 if host == "localhost" else 27017
    password = os.environ.get("DB_PASSWORD", "hunter2")
    user_name = "AzureDiamond"
    return f"mongodb://{user_name}:{password}@{host}:{port}"
