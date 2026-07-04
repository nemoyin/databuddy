"""Tests for config system (TC-1.2 ~ TC-1.6) and CORS middleware."""
from __future__ import annotations

import os
import pytest
from httpx import AsyncClient, ASGITransport
from jwbuddy.main import app
from jwbuddy.config import Settings


class TestConfigDefaults:
    """TC-1.2, TC-1.3, TC-1.6: Environment variable loading and defaults."""

    def test_debug_env_var_enabled(self, monkeypatch):
        """TC-1.2: Setting JWB_DEBUG=true enables debug mode."""
        monkeypatch.setenv("JWB_DEBUG", "true")
        s = Settings()
        assert s.debug is True

    def test_debug_env_var_disabled(self, monkeypatch):
        """TC-1.2 variant: JWB_DEBUG=false disables debug mode."""
        monkeypatch.setenv("JWB_DEBUG", "false")
        s = Settings()
        assert s.debug is False

    def test_missing_optional_config_defaults(self, monkeypatch):
        """TC-1.3: Missing JWB_LLM_CLOUD_API_KEY should not prevent startup."""
        # Ensure the variable is NOT set
        monkeypatch.delenv("JWB_LLM_CLOUD_API_KEY", raising=False)
        s = Settings()
        # Should use default empty string
        assert s.llm_cloud_api_key == ""

    def test_jwb_prefix_enforcement(self, monkeypatch):
        """TC-1.6: Only JWB_ prefixed env vars are recognized."""
        # Set a non-JWB variable
        monkeypatch.setenv("NOT_JWB_DEBUG", "true")
        monkeypatch.setenv("JWB_DEBUG", "false")
        s = Settings()
        # The non-JWB var should be ignored
        assert s.debug is False  # JWB_DEBUG takes precedence

    def test_default_values(self, monkeypatch):
        """Verify sensible defaults are used."""
        # Clear relevant env vars
        for key in list(os.environ.keys()):
            if key.startswith("JWB_"):
                monkeypatch.delenv(key, raising=False)
        s = Settings()
        assert s.app_name == "JWBuddy"
        assert s.port == 8000
        assert s.sql_readonly_enabled is True
        assert s.llm_fallback_enabled is True


class TestCORS:
    """TC-1.4, TC-1.5: CORS middleware behavior."""

    @pytest.mark.asyncio
    async def test_cors_allowed_origin(self):
        """TC-1.4: Allowed origin returns access-control-allow-origin header."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.options(
                "/health",
                headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
            )
        # CORS middleware should allow this origin
        assert resp.status_code in (200, 204)
        allow_origin = resp.headers.get("access-control-allow-origin")
        assert allow_origin == "http://localhost:3000"

    @pytest.mark.asyncio
    async def test_cors_allowed_origin_5173(self):
        """TC-1.4 variant: localhost:5173 (Vite dev server) is allowed."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.options(
                "/health",
                headers={"Origin": "http://localhost:5173", "Access-Control-Request-Method": "GET"},
            )
        assert resp.status_code in (200, 204)
        assert resp.headers.get("access-control-allow-origin") == "http://localhost:5173"

    @pytest.mark.asyncio
    async def test_cors_disallowed_origin(self):
        """TC-1.5: Disallowed origin returns no CORS allow-origin."""
        transport = ASGITransport(app=app)
        async with AsyncClient(transport=transport, base_url="http://test") as client:
            resp = await client.options(
                "/health",
                headers={"Origin": "http://evil.com", "Access-Control-Request-Method": "GET"},
            )
        # Disallowed origin: no access-control-allow-origin header, or 400
        allow_origin = resp.headers.get("access-control-allow-origin")
        # FastAPI CORS either omits the header or returns status 400
        assert allow_origin is None or resp.status_code == 400
