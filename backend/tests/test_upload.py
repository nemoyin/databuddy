"""Tests for file upload API (TC-6.1 ~ TC-6.8)."""
from __future__ import annotations

import io
import os
import tempfile
import pytest
from httpx import AsyncClient, ASGITransport
from jwbuddy.main import app


@pytest.mark.asyncio
async def test_upload_excel():
    """TC-6.1: Upload Excel .xlsx returns {filename, file_path, size}."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        content = b"fake xlsx content"
        resp = await client.post(
            "/upload",
            files={"file": ("test_data.xlsx", io.BytesIO(content), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "test_data.xlsx"
    assert data["file_path"].endswith("test_data.xlsx")
    assert data["size"] == len(content)


@pytest.mark.asyncio
async def test_upload_pdf():
    """TC-6.2: Upload PDF .pdf returns file info."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        content = b"fake pdf content"
        resp = await client.post(
            "/upload",
            files={"file": ("report.pdf", io.BytesIO(content), "application/pdf")},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "report.pdf"
    assert data["size"] == len(content)


@pytest.mark.asyncio
async def test_upload_csv():
    """TC-6.3: Upload CSV .csv returns file info."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        content = b"name,age\nAlice,30\n"
        resp = await client.post(
            "/upload",
            files={"file": ("users.csv", io.BytesIO(content), "text/csv")},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "users.csv"
    assert data["size"] == len(content)


@pytest.mark.asyncio
async def test_upload_docx():
    """TC-6.4: Upload Word .docx returns file info."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        content = b"fake docx content"
        resp = await client.post(
            "/upload",
            files={"file": ("document.docx", io.BytesIO(content), "application/vnd.openxmlformats-officedocument.wordprocessingml.document")},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "document.docx"
    assert data["size"] == len(content)


@pytest.mark.asyncio
async def test_upload_image_png():
    """TC-6.5: Upload image .png returns file info."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        content = b"fake png content"
        resp = await client.post(
            "/upload",
            files={"file": ("photo.png", io.BytesIO(content), "image/png")},
        )
    assert resp.status_code == 200
    data = resp.json()
    assert data["filename"] == "photo.png"


@pytest.mark.asyncio
async def test_upload_reject_unsupported_extension():
    """TC-6.6: Reject unsupported format .exe returns 400."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        content = b"malicious"
        resp = await client.post(
            "/upload",
            files={"file": ("virus.exe", io.BytesIO(content), "application/octet-stream")},
        )
    assert resp.status_code == 400
    assert "不支持的文件类型" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_upload_file_too_large(monkeypatch):
    """TC-6.7: File exceeding size limit returns 400."""
    import jwbuddy.api.upload as upload_mod
    # Temporarily lower limit to 10 bytes for testing
    monkeypatch.setattr(upload_mod, "MAX_FILE_SIZE", 10)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        content = b"x" * 100  # 100 bytes > 10 byte limit
        resp = await client.post(
            "/upload",
            files={"file": ("big.csv", io.BytesIO(content), "text/csv")},
        )
    assert resp.status_code == 400
    assert "超过" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_upload_path_security():
    """TC-6.8: Uploaded file saved to data/uploads/ without path traversal."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        content = b"safe content"
        # Use a valid extension with path traversal in the filename
        resp = await client.post(
            "/upload",
            files={"file": ("../etc/malicious.csv", io.BytesIO(content), "text/csv")},
        )
    assert resp.status_code == 200
    data = resp.json()
    # The saved name must NOT contain ".." (path traversal neutralized)
    assert ".." not in data["file_path"]
    # The original filename is reported as-is
    assert data["filename"] == "../etc/malicious.csv"
    # The file_path should be safe (inside uploads dir, no traversal)
    saved_path = data["file_path"]
    assert not saved_path.startswith("..")
    assert "/etc/" not in saved_path
