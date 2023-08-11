import pytest


@pytest.mark.django_db
def test_show_date_logs(auto_login_staff):
    """
    Test get show date logs
    """
    client, user = auto_login_staff()
    response = client.get("/admin/show-date-logs", follow=True)
    assert response.status_code == 200
    assert response.template_name == ["sortlogs/show_date_logs.html"]


def test_load_data():
    """
    Just load some data to database and check if they exist in mongodb
    """
    assert True


@pytest.mark.django_db
def test_show_date_logs_post(auto_login_staff, create_input_data_mongo):
    """
    Test post show date logs
    """
    client, user = auto_login_staff()
    data = {
        "level": "log",
        "category": "nginx",
        "domain": "example",
        "port": "443",
        "date": "*",
    }
    response = client.post("/admin/show-date-logs/", data=data, follow=False)
    assert response.status_code == 200
    assert response.template_name == ["sortlogs/show_date_logs.html"]

    expected = (
        b'<tr><td><a href="/admin/show-logs/?pattern=log_nginx_example_443_2021-08-22">'
        b"log_nginx_example_443_2021-08-22</a></td><td>00:00:58</td><td>00:01:16</td><td>3</td>"
        b"</tr>"
    )
    assert expected in response.content


@pytest.mark.django_db
def test_show_logs(auto_login_staff):
    """
    Test get show logs
    """
    client, user = auto_login_staff()
    response = client.get(
        "/admin/show-logs/?pattern=log_nginx_example_443_2021-08-22",
        follow=True,
    )
    assert response.status_code == 200
    assert response.template_name == ["sortlogs/show_logs.html"]

    expected = (
        b'<div>1.2.3.4 - - [22/Aug/2021:00:00:58 +0000] "GET / HTTP/1.1" 200\n</div>'
        b'<div>1.2.3.4 - - [22/Aug/2021:00:00:59 +0000] "GET /pl HTTP/1.1" 200\n</div>'
        b'<div>4.3.2.1 - - [22/Aug/2021:00:01:16 +0000] "GET /mysite.html HTTP/1.1" 200\n</div>'
    )

    assert expected in response.content


@pytest.mark.django_db
def test_graph_logs(auto_login_staff):
    """
    Test get graph
    """
    client, user = auto_login_staff()
    response = client.get("/admin/graph-logs", follow=True)
    assert response.status_code == 200
    assert response.template_name == ["sortlogs/graph_logs.html"]
