import pytest


@pytest.mark.django_db
def test_search_logs_request(auto_login_staff):
    """
    Test get form "search_logs" page
    """
    client, user = auto_login_staff()
    response = client.get("/admin/search-logs", follow=True)
    assert response.status_code == 200
    assert response.template_name == ["sortlogs/search_logs.html"]


@pytest.mark.django_db
def test_showtables_request(auto_login_staff):
    """
    Test get show tables
    """
    client, user = auto_login_staff()
    response = client.get("/admin/show-tables", follow=True)
    assert response.status_code == 200
    assert response.template_name == ["sortlogs/show_tables.html"]


@pytest.mark.django_db
def test_show_loaded_files_request(auto_login_staff):
    """
    Test show all tables and show loaded file from specified table.
    """
    client, user = auto_login_staff()
    response = client.get("/admin/show-loaded-files?table=log_nginx_example_443", follow=True)
    assert response.status_code == 200
    assert response.template_name == ["sortlogs/show_loaded_files.html"]


@pytest.mark.django_db
def test_graph_logs_request(auto_login_staff):
    """
    Test get show date logs
    """
    client, user = auto_login_staff()
    response = client.get("/admin/graph-logs", follow=True)
    assert response.status_code == 200
    assert response.template_name == ["sortlogs/graph_logs.html"]


@pytest.mark.django_db
def test_show_date_logs_post(auto_login_staff, create_input_data_mongo):
    """
    Test post show date logs
    """
    client, user = auto_login_staff()
    data = {
        "table": "log_nginx_example_443",
        "start_datetime": "2021-08-17 12:50:59",
        "end_datetime": "2021-08-30 23:59:59",
        "limit": "1",
    }
    response = client.post("/admin/search-logs/", data=data, follow=False)
    assert response.status_code == 200

    errors_str = ''
    if hasattr(response, 'context_data'):
        for name, errors in response.context_data['form'].errors.items():
            errors_str = f"{errors_str}\nError in field {name}."
            for e in errors:
                errors_str = f"{errors_str}\n{e}"

    assert '' == errors_str

    expected = (
        b'<select name="table" id="id_table">\n  <option value="log_nginx_example_443" selected>'
        b'log_nginx_example_443</option>\n\n</select>'
    )
    assert expected in response.content

    expected2 = (
        b'<div>1.2.3.4 - - [22/Aug/2021:00:00:58 +0000] &quot;GET / HTTP/1.1&quot; 200</div>'
    )
    assert expected2 in response.content


@pytest.mark.django_db
def test_graph_logs(auto_login_staff):
    """
    Test get graph
    """
    client, user = auto_login_staff()
    response = client.get("/admin/graph-logs", follow=True)
    assert response.status_code == 200
    assert response.template_name == ["sortlogs/graph_logs.html"]
