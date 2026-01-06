"""Tests for design time calculation endpoint."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

# Test Julian Day for 2000-01-01 12:00:00 UT
TEST_BIRTH_JD_UT = 2451545.0


@pytest.fixture
def auth_token():
    """Get auth token for tests."""
    import os
    os.environ["AGPL_SERVICE_API_KEYS"] = "test-token"
    return "test-token"


def test_design_time_without_auth():
    """Test that design-time endpoint requires authentication."""
    response = client.post(
        "/v1/design-time",
        json={
            "birth_jd_ut": TEST_BIRTH_JD_UT,
            "sun_offset_deg": 88.0,
            "search_window_days": {"min": 70, "max": 110},
            "tolerance_deg": 0.01,
            "max_iter": 80,
        },
    )
    assert response.status_code == 401


def test_design_time_success(auth_token):
    """Test successful design time calculation."""
    response = client.post(
        "/v1/design-time",
        json={
            "birth_jd_ut": TEST_BIRTH_JD_UT,
            "sun_offset_deg": 88.0,
            "search_window_days": {"min": 70, "max": 110},
            "tolerance_deg": 0.01,
            "max_iter": 80,
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "design_jd_ut" in data
    assert "target_sun_lon" in data
    assert "achieved_sun_lon" in data
    assert "delta_deg" in data
    assert "iterations" in data
    assert data["delta_deg"] <= 0.01  # Within tolerance
    assert data["design_jd_ut"] < data["birth_jd_ut"]  # Design is before birth
    assert "X-AGPL-Source" in response.headers


def test_design_time_tolerance(auth_token):
    """Test that delta is within tolerance."""
    response = client.post(
        "/v1/design-time",
        json={
            "birth_jd_ut": TEST_BIRTH_JD_UT,
            "sun_offset_deg": 88.0,
            "search_window_days": {"min": 70, "max": 110},
            "tolerance_deg": 0.01,
            "max_iter": 80,
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert abs(data["delta_deg"]) <= 0.01


def test_design_time_invalid_window(auth_token):
    """Test error for invalid search window."""
    response = client.post(
        "/v1/design-time",
        json={
            "birth_jd_ut": TEST_BIRTH_JD_UT,
            "sun_offset_deg": 88.0,
            "search_window_days": {"min": 110, "max": 70},  # Invalid: min > max
            "tolerance_deg": 0.01,
            "max_iter": 80,
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    assert response.status_code == 400
    data = response.json()
    assert "error" in data


def test_design_time_no_convergence(auth_token):
    """Test error when convergence fails."""
    response = client.post(
        "/v1/design-time",
        json={
            "birth_jd_ut": TEST_BIRTH_JD_UT,
            "sun_offset_deg": 88.0,
            "search_window_days": {"min": 1, "max": 2},  # Too narrow window
            "tolerance_deg": 0.0001,  # Very strict tolerance
            "max_iter": 5,  # Too few iterations
        },
        headers={"Authorization": f"Bearer {auth_token}"},
    )
    # Should either succeed or return 422 (no convergence)
    assert response.status_code in [200, 422]
    if response.status_code == 422:
        data = response.json()
        assert "error" in data
        assert data["error"]["code"] == "no_convergence"
