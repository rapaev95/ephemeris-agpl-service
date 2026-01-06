"""Tests for houses calculation endpoint."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test Julian Day for 2000-01-01 12:00:00 UT
TEST_JD_UT = 2451545.0
# São Paulo coordinates
TEST_LAT = -23.5505
TEST_LON = -46.6333


@pytest.fixture
def auth_token():
    """Get auth token for tests."""
    import os
    os.environ["AGPL_SERVICE_API_KEYS"] = "test-token"
    return "test-token"


def test_houses_without_auth():
    """Test that houses endpoint requires authentication."""
    response = client.post(
        "/v1/houses",
        json={
            "jd_ut": TEST_JD_UT,
            "lat": TEST_LAT,
            "lon": TEST_LON,
            "house_system": "P",
        },
    )
    assert response.status_code == 401


def test_houses_placidus(auth_token):
    """Test calculating houses with Placidus system."""
    response = client.post(
        "/v1/houses",
        json={
            "jd_ut": TEST_JD_UT,
            "lat": TEST_LAT,
            "lon": TEST_LON,
            "house_system": "P",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "cusps" in data
    assert "angles" in data
    assert len(data["cusps"]) == 13
    assert data["cusps"][0] == 0  # First cusp is always 0
    assert "asc" in data["angles"]
    assert "mc" in data["angles"]
    assert 0 <= data["angles"]["asc"] < 360
    assert 0 <= data["angles"]["mc"] < 360
    assert "X-AGPL-Source" in response.headers


def test_houses_cusps_normalized(auth_token):
    """Test that all cusps are normalized to [0, 360)."""
    response = client.post(
        "/v1/houses",
        json={
            "jd_ut": TEST_JD_UT,
            "lat": TEST_LAT,
            "lon": TEST_LON,
            "house_system": "P",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    for cusp in data["cusps"]:
        assert 0 <= cusp < 360


def test_houses_unsupported_system(auth_token):
    """Test error for unsupported house system."""
    response = client.post(
        "/v1/houses",
        json={
            "jd_ut": TEST_JD_UT,
            "lat": TEST_LAT,
            "lon": TEST_LON,
            "house_system": "X",
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "invalid_house_system"


def test_houses_different_systems(auth_token):
    """Test different house systems."""
    systems = ["P", "K", "R", "C", "E"]
    for system in systems:
        response = client.post(
            "/v1/houses",
            json={
                "jd_ut": TEST_JD_UT,
                "lat": TEST_LAT,
                "lon": TEST_LON,
                "house_system": system,
            },
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["house_system"] == system
        assert len(data["cusps"]) == 13
