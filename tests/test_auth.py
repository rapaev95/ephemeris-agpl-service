"""Tests for authentication."""

import pytest
import os
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_no_auth():
    """Test that health endpoint doesn't require auth."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_version_no_auth():
    """Test that version endpoint doesn't require auth."""
    response = client.get("/v1/version")
    assert response.status_code == 200
    data = response.json()
    assert "service" in data
    assert "api_version" in data


def test_source_no_auth():
    """Test that source endpoint doesn't require auth."""
    response = client.get("/v1/source")
    assert response.status_code == 200
    data = response.json()
    assert "license" in data
    assert "repo" in data
    assert data["license"] == "AGPL-3.0"


def test_positions_without_token():
    """Test that positions endpoint requires token."""
    os.environ["AGPL_SERVICE_API_KEYS"] = "test-token"
    response = client.post(
        "/v1/positions",
        json={
            "jd_ut": 2451545.0,
            "bodies": ["Sun"],
        },
    )
    assert response.status_code == 401


def test_positions_invalid_token():
    """Test that invalid token is rejected."""
    os.environ["AGPL_SERVICE_API_KEYS"] = "test-token"
    response = client.post(
        "/v1/positions",
        json={
            "jd_ut": 2451545.0,
            "bodies": ["Sun"],
        },
        headers={"Authorization": "Bearer invalid-token"},
    )
    assert response.status_code == 401


def test_positions_valid_token():
    """Test that valid token is accepted."""
    os.environ["AGPL_SERVICE_API_KEYS"] = "test-token"
    response = client.post(
        "/v1/positions",
        json={
            "jd_ut": 2451545.0,
            "bodies": ["Sun"],
        },
        headers={"Authorization": "Bearer test-token"},
    )
    assert response.status_code == 200


def test_positions_multiple_keys():
    """Test that multiple keys work (comma-separated)."""
    os.environ["AGPL_SERVICE_API_KEYS"] = "key1,key2,key3"
    # Test with first key
    response = client.post(
        "/v1/positions",
        json={
            "jd_ut": 2451545.0,
            "bodies": ["Sun"],
        },
        headers={"Authorization": "Bearer key1"},
    )
    assert response.status_code == 200

    # Test with second key
    response = client.post(
        "/v1/positions",
        json={
            "jd_ut": 2451545.0,
            "bodies": ["Sun"],
        },
        headers={"Authorization": "Bearer key2"},
    )
    assert response.status_code == 200

    # Test with third key
    response = client.post(
        "/v1/positions",
        json={
            "jd_ut": 2451545.0,
            "bodies": ["Sun"],
        },
        headers={"Authorization": "Bearer key3"},
    )
    assert response.status_code == 200
