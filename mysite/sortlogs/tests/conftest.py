from pathlib import Path

from django.contrib.auth.models import User
import pytest


@pytest.fixture
def auto_login_staff(client):
    def make_auto_login_staff():
        user = User.objects.create(
            username="admin",
            first_name="Wojciech",
            last_name="Zajac",
            is_staff=True,
        )
        user.set_password("vgy7*UHB")
        user.save()
        client.login(username=user, password="vgy7*UHB")
        return client, user

    return make_auto_login_staff


example_com_data = """1.2.3.4 - - [22/Aug/2021:00:00:58 +0000] "GET / HTTP/1.1" 200"
1.2.3.4 - - [22/Aug/2021:00:00:59 +0000] "GET /pl HTTP/1.1" 200"
4.3.2.1 - - [22/Aug/2021:00:01:16 +0000] "GET /mysite.html HTTP/1.1" 200"
"""


@pytest.fixture
def create_logs_file():
    file_path = Path("example.com-443-access.log.0")
    if not file_path.exists():
        with open(file_path, "wt") as f:
            f.write(example_com_data)


@pytest.fixture
def create_input_data_mongo(mongodb):
    value = '{"first_log_time": "00:00:58", "last_log_time": "00:01:16", "lines_number": 3}'
    mongodb.base_keys.insert_one({"log_nginx_example_443_2021-08-22": value})
    assert "base_keys" in mongodb.list_collection_names()

    logs = example_com_data.rstrip().split("\n")
    collection = mongodb.get_collection("log_nginx_example_443")
    collection.insert_one({"2021-08-22": logs})
