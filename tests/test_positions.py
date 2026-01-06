"""Tests for positions calculation endpoint."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test Julian Day for 2000-01-01 12:00:00 UT
TEST_JD_UT = 2451545.0


@pytest.fixture
def auth_token():
    """Get auth token for tests."""
    import os
    os.environ["AGPL_SERVICE_API_KEYS"] = "test-token"
    return "test-token"


def test_positions_without_auth():
    """Test that positions endpoint requires authentication."""
    response = client.post(
        "/v1/positions",
        json={
            "jd_ut": TEST_JD_UT,
            "bodies": ["Sun"],
        },
    )
    assert response.status_code == 401


def test_positions_sun(auth_token):
    """Test calculating Sun position."""
    response = client.post(
        "/v1/positions",
        json={
            "jd_ut": TEST_JD_UT,
            "bodies": ["Sun"],
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "positions" in data
    assert "Sun" in data["positions"]
    assert 0 <= data["positions"]["Sun"] < 360
    assert "X-AGPL-Source" in response.headers


def test_positions_multiple_bodies(auth_token):
    """Test calculating multiple body positions."""
    response = client.post(
        "/v1/positions",
        json={
            "jd_ut": TEST_JD_UT,
            "bodies": ["Sun", "Moon", "Mercury", "Venus", "Mars"],
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "positions" in data
    assert len(data["positions"]) == 5
    for body in ["Sun", "Moon", "Mercury", "Venus", "Mars"]:
        assert body in data["positions"]
        assert 0 <= data["positions"][body] < 360


def test_positions_all_bodies(auth_token):
    """Test calculating all supported bodies."""
    bodies = [
        "Sun",
        "Moon",
        "Mercury",
        "Venus",
        "Mars",
        "Jupiter",
        "Saturn",
        "Uranus",
        "Neptune",
        "Pluto",
        "TrueNode",
    ]
    response = client.post(
        "/v1/positions",
        json={
            "jd_ut": TEST_JD_UT,
            "bodies": bodies,
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["positions"]) == len(bodies)
    for body in bodies:
        assert 0 <= data["positions"][body] < 360


def test_positions_unsupported_body(auth_token):
    """Test error for unsupported body."""
    response = client.post(
        "/v1/positions",
        json={
            "jd_ut": TEST_JD_UT,
            "bodies": ["Lilith"],
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 400
    data = response.json()
    assert "error" in data
    assert data["error"]["code"] == "unsupported_body"


def test_positions_normalized_range(auth_token):
    """Test that all positions are normalized to [0, 360)."""
    response = client.post(
        "/v1/positions",
        json={
            "jd_ut": TEST_JD_UT,
            "bodies": ["Sun", "Moon", "Mercury", "Venus", "Mars"],
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    for body, position in data["positions"].items():
        assert isinstance(position, (int, float))
        assert 0 <= position < 360


def test_positions_meta(auth_token):
    """Test that response includes metadata."""
    response = client.post(
        "/v1/positions",
        json={
            "jd_ut": TEST_JD_UT,
            "bodies": ["Sun"],
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "meta" in data
    assert data["meta"]["engine"] == "swisseph"
    assert "sidereal" in data["meta"]
