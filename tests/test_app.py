import pytest
from app import app


@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


# -------------------------
# ROOT ENDPOINT TESTS
# -------------------------

def test_home_success(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.is_json
    assert response.json == {"message": "this is test deplyoment"}


def test_home_content_type(client):
    response = client.get("/")
    assert response.headers["Content-Type"] == "application/json"


def test_home_response_structure(client):
    response = client.get("/")
    data = response.get_json()
    assert "message" in data
    assert isinstance(data["message"], str)


# -------------------------
# HELLO ENDPOINT TESTS
# -------------------------

def test_hello_valid_name(client):
    response = client.get("/hello/Deepak")
    assert response.status_code == 200
    assert response.json == {"message": "Hello Deepak"}


def test_hello_different_name(client):
    response = client.get("/hello/Alice")
    assert response.status_code == 200
    assert response.json["message"] == "Hello Alice"


def test_hello_numeric_name(client):
    response = client.get("/hello/123")
    assert response.status_code == 200
    assert response.json["message"] == "Hello 123"


def test_hello_special_characters(client):
    response = client.get("/hello/test-user")
    assert response.status_code == 200
    assert response.json["message"] == "Hello test-user"


def test_hello_long_name(client):
    name = "a" * 100
    response = client.get(f"/hello/{name}")
    assert response.status_code == 200
    assert response.json["message"] == f"Hello {name}"


def test_hello_empty_name_not_allowed(client):
    response = client.get("/hello/")
    assert response.status_code in [404, 405]


# -------------------------
# INVALID ROUTE TESTS
# -------------------------

def test_invalid_route(client):
    response = client.get("/invalid")
    assert response.status_code == 404


def test_random_route(client):
    response = client.get("/randomendpoint")
    assert response.status_code == 404


# -------------------------
# METHOD VALIDATION TESTS
# -------------------------

def test_home_post_not_allowed(client):
    response = client.post("/")
    assert response.status_code in [405, 404]


def test_hello_post_not_allowed(client):
    response = client.post("/hello/test")
    assert response.status_code in [405, 404]


# -------------------------
# RESPONSE FORMAT TESTS
# -------------------------

def test_home_json_format(client):
    response = client.get("/")
    assert isinstance(response.get_json(), dict)


def test_hello_json_format(client):
    response = client.get("/hello/Test")
    assert isinstance(response.get_json(), dict)


def test_hello_message_field_exists(client):
    response = client.get("/hello/Tester")
    data = response.get_json()
    assert "message" in data


# -------------------------
# CASE SENSITIVITY TESTS
# -------------------------

def test_case_sensitive_name(client):
    response = client.get("/hello/deepak")
    assert response.status_code == 200
    assert response.json["message"] == "Hello deepak"


# -------------------------
# URL ENCODING TESTS
# -------------------------

def test_url_encoded_name(client):
    response = client.get("/hello/John%20Doe")
    assert response.status_code == 200
    assert response.json["message"] == "Hello John Doe"


# -------------------------
# STRESS / MULTIPLE CALL TEST
# -------------------------

def test_multiple_requests(client):
    for i in range(10):
        response = client.get("/hello/test")
        assert response.status_code == 200
        assert response.json["message"] == "Hello test"