import pytest
from httpx import AsyncClient, ASGITransport
from jwbuddy.main import app


@pytest.mark.asyncio
async def test_chat_no_session():
    """TC-5.4: Chat with invalid session_id returns 404."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/chat", json={
            "session_id": "nonexistent",
            "message": "hello",
        })
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_create_session():
    """TC-5.1: Create session returns id, title, etc."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.post("/sessions", json={"title": "test"})
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data
    assert data["title"] == "test"


@pytest.mark.asyncio
async def test_list_sessions():
    """TC-5.2: List sessions returns a list."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/sessions")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_chat_with_files_parameter():
    """TC-5.5: Upload file context passed in chat request body."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # First create a session
        create_resp = await client.post("/sessions", json={"title": "file-chat-test"})
        session_id = create_resp.json()["id"]

        # Send chat message with files parameter
        resp = await client.post("/chat", json={
            "session_id": session_id,
            "message": "分析这个表格",
            "files": ["test_data.xlsx"],
        })
        # SSE streaming should succeed (200 with text/event-stream)
        assert resp.status_code == 200
        assert "text/event-stream" in resp.headers.get("content-type", "")
        # Read first few SSE events to verify it doesn't crash
        content = resp.text[:500]
        assert "event:" in content or "data:" in content
