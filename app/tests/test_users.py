from fastapi.testclient import TestClient
from app.main import app
from app.db.base import Base, engine

client = TestClient(app)

def setup_module():
    Base.metadata.create_all(bind=engine)

def teardown_module():
    Base.metadata.drop_all(bind=engine)

def test_create_user():
    response = client.post(
        "/api/v1/users/",
        json={
            "email": "test@example.com",
            "password": "testpassword",
            "is_active": True,
            "is_superuser": False,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data

def test_read_users():
    response = client.get("/api/v1/users/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_read_user():
    # First create a user
    create_response = client.post(
        "/api/v1/users/",
        json={
            "email": "test2@example.com",
            "password": "testpassword",
            "is_active": True,
            "is_superuser": False,
        },
    )
    user_id = create_response.json()["id"]
    
    # Then read the user
    response = client.get(f"/api/v1/users/{user_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == "test2@example.com"
    assert data["id"] == user_id 