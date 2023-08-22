import datetime
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


example_com_data = """5.6.7.8 - - [17/Nov/2020:06:55:53 +0000] "GET / HTTP/1.1" 200
5.6.7.8 - - [18/Nov/2020:01:27:59 +0000] "GET /pl HTTP/1.1" 200
4.4.5.5 - - [20/Nov/2020:18:51:16 +0000] "GET /mysite.html HTTP/1.1" 200
"""


@pytest.fixture
def create_logs_file():
    file_path = Path("mysite/sortlogs/tests/fixtures/example.com-80-access.log.0")
    if not file_path.exists():
        with open(file_path, "wt") as f:
            f.write(example_com_data)


@pytest.fixture
def create_input_data_mongo(mongodb):
    mongodb.log_nginx_example_443.insert_many([{
        "datetime": datetime.datetime(year=2021, month=8, day=22, hour=0, minute=0, second=58),
        "line": '1.2.3.4 - - [22/Aug/2021:00:00:58 +0000] "GET / HTTP/1.1" 200',
    },{
        "datetime": datetime.datetime(year=2021, month=8, day=22, hour=0, minute=0, second=59),
        "line": '1.2.3.4 - - [22/Aug/2021:00:00:59 +0000] "GET /pl HTTP/1.1" 200',
    },{
        "datetime": datetime.datetime(year=2021, month=8, day=22, hour=0, minute=1, second=16),
        "line": '4.3.2.1 - - [22/Aug/2021:00:01:16 +0000] "GET /mysite.html HTTP/1.1" 200',
    }])
