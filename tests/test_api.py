import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from api.database import Base, get_db
from api.main import app

HOUSE = {
    "bedrooms": 3,
    "bathrooms": 2.5,
    "sqft_living": 1800,
    "grade": 8,
    "zipcode": "98103",
}


@pytest.fixture
def client():
    # StaticPool keeps one shared connection, so the in-memory DB survives across requests.
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)

    def override_get_db():
        with TestingSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_house_returns_201_with_id(client):
    response = client.post("/houses", json=HOUSE)
    assert response.status_code == 201
    assert response.json() == {"id": 1, **HOUSE}


def test_create_house_with_invalid_grade_returns_422(client):
    response = client.post("/houses", json={**HOUSE, "grade": 99})
    assert response.status_code == 422


def test_create_house_with_missing_field_returns_422(client):
    incomplete = {k: v for k, v in HOUSE.items() if k != "zipcode"}
    assert client.post("/houses", json=incomplete).status_code == 422


def test_list_houses_empty(client):
    assert client.get("/houses").json() == []


def test_list_houses_ordered_by_id(client):
    client.post("/houses", json=HOUSE)
    client.post("/houses", json={**HOUSE, "bedrooms": 4})
    result = client.get("/houses").json()
    assert [h["id"] for h in result] == [1, 2]
    assert result[1]["bedrooms"] == 4


def test_get_house(client):
    client.post("/houses", json=HOUSE)
    response = client.get("/houses/1")
    assert response.status_code == 200
    assert response.json() == {"id": 1, **HOUSE}


def test_get_missing_house_returns_404(client):
    assert client.get("/houses/999").status_code == 404


def test_update_house_replaces_fields(client):
    client.post("/houses", json=HOUSE)
    changed = {**HOUSE, "bedrooms": 5, "zipcode": "98004"}
    response = client.put("/houses/1", json=changed)
    assert response.status_code == 200
    assert response.json() == {"id": 1, **changed}
    assert client.get("/houses/1").json()["bedrooms"] == 5


def test_update_missing_house_returns_404(client):
    assert client.put("/houses/999", json=HOUSE).status_code == 404


def test_update_house_with_invalid_data_returns_422(client):
    client.post("/houses", json=HOUSE)
    assert client.put("/houses/1", json={**HOUSE, "grade": 0}).status_code == 422


def test_delete_house_returns_204_and_removes_it(client):
    client.post("/houses", json=HOUSE)
    assert client.delete("/houses/1").status_code == 204
    assert client.get("/houses/1").status_code == 404


def test_delete_missing_house_returns_404(client):
    assert client.delete("/houses/999").status_code == 404
