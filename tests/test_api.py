from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/health")
    assert response.status_code == 200
    payload = response.json()
    assert payload.get("status") == "ok"
    assert payload.get("service") == "job-tailor-agent"


def test_version_endpoint() -> None:
    response = client.get("/version")
    assert response.status_code == 200
    payload = response.json()
    assert "version" in payload
    assert "llm_configured" in payload


def test_memory_and_search_flow() -> None:
    items = [
        {"label": "skill", "text": "agentic workflows with FastAPI"},
        {"label": "project", "text": "multi-agent job tailoring system"},
        {"label": "publication", "text": "wrote about embeddings and retrieval"},
    ]
    ingest_resp = client.post("/memory", json={"items": items})
    assert ingest_resp.status_code == 200
    ids = ingest_resp.json()
    assert len(ids) == len(items)

    search_resp = client.post("/memory/search", json={"query": "agentic workflows", "top_k": 2})
    assert search_resp.status_code == 200
    results = search_resp.json()
    assert 0 < len(results) <= 2
    for hit in results:
        assert {"id", "text", "score", "metadata"} <= hit.keys()


def test_process_endpoint_with_job_text() -> None:
    payload = {
        "job_text": "We need someone to design agentic workflows and build FastAPI services.",
        "top_k": 2,
        "profile_items": [
            {
                "label": "skill",
                "text": "Designed agentic workflows for job applications.",
            }
        ],
    }
    response = client.post("/process", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert isinstance(body.get("requirements"), list)
    assert isinstance(body.get("plan"), list)
    assert isinstance(body.get("matches"), list)
    packet = body.get("packet") or {}
    assert isinstance(packet.get("cover_letter"), str)
    assert isinstance(packet.get("tailored_bullets"), list)
    assert isinstance(packet.get("talking_points"), list)


def test_process_requires_job_text_or_url() -> None:
    response = client.post("/process", json={"profile_items": []})
    assert response.status_code == 400

