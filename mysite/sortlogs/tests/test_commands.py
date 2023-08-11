import pytest

from .conftest import example_com_data
from ..mongo.logs_load import Loader


@pytest.mark.django_db
def test_load_file_logs(mongodb, create_logs_file):
    """
    Test Loader.load_file_logs method which is main method for load_logs command
    """
    filename = "example.com-443-access.log.0"
    loader = Loader()
    loader.db = mongodb
    loader.load_file_logs(filename)

    collection = loader.db.get_collection("log_nginx_example_443")
    result = "".join(d["line"] for d in collection.find())

    assert result == example_com_data
