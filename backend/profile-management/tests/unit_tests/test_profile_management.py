import pytest
from fastapi.testclient import TestClient
from main import app, Base, engine, SessionLocal, Profile

@pytest.fixture(autouse=True)
def setup_and_teardown_db():
    # Create tables
    Base.metadata.create_all(bind=engine)
    # Clear data before each test
    db = SessionLocal()
    db.query(Profile).delete()
    db.commit()
    db.close()
    yield
    # Drop tables after test if needed
    # Base.metadata.drop_all(bind=engine)

client = TestClient(app)

def test_profiles_query_empty():
    query = """
    query {
        profiles {
            id
            name
            email
            address
        }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    assert response.json()["data"]["profiles"] == []

def test_profiles_query_with_data():
    # Insert a profile
    db = SessionLocal()
    profile = Profile(name="Alice", email="alice@example.com", address="Wonderland")
    db.add(profile)
    db.commit()
    db.refresh(profile)
    db.close()

    query = """
    query {
        profiles {
            id
            name
            email
            address
        }
    }
    """
    response = client.post("/graphql", json={"query": query})
    assert response.status_code == 200
    data = response.json()["data"]["profiles"]
    assert len(data) == 1
    assert data[0]["name"] == "Alice"
    assert data[0]["email"] == "alice@example.com"
    assert data[0]["address"] == "Wonderland"