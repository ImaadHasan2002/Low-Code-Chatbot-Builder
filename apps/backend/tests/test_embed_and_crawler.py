from pathlib import Path

from app.models.knowledge_base import KnowledgeBase
from app.utils.scraping import CrawledPage


async def _make_workspace(auth_client, name="Crawler WS"):
    resp = await auth_client.post("/api/v1/workspaces/", json={"name": name})
    assert resp.status_code == 200, resp.text
    return resp.json()["_id"]


async def test_chatbot_script_served_from_backend(client):
    resp = await client.get("/chatbot.js")

    assert resp.status_code == 200
    assert "application/javascript" in resp.headers["content-type"]
    assert "data-workspace-id" in resp.text
    assert "workspace_id" in resp.text
    assert "/api/v1/playground/chat" in resp.text

    fixture = Path(__file__).parent / "fixtures" / "external-embed.html"
    assert 'src="http://localhost:8000/chatbot.js"' in fixture.read_text()
    assert 'data-workspace-id="WORKSPACE_ID"' in fixture.read_text()


async def test_theme_update_accepts_camel_case(auth_client):
    ws_id = await _make_workspace(auth_client, "Theme Camel")

    resp = await auth_client.put(
        f"/api/v1/theme/?workspace_id={ws_id}",
        json={"primaryColor": "#ff0000", "showHeader": False},
    )

    assert resp.status_code == 200, resp.text
    assert resp.json()["primary_color"] == "#ff0000"
    assert resp.json()["show_header"] is False


async def test_background_crawl_stores_page_records(auth_client, monkeypatch):
    ws_id = await _make_workspace(auth_client)
    pages = [
        CrawledPage(
            url="https://example.com/",
            title="Home",
            content="Welcome to Example Company.",
            depth=0,
            status_code=200,
        ),
        CrawledPage(
            url="https://example.com/pricing",
            title="Pricing",
            content="Pricing starts at ten dollars.",
            depth=1,
            status_code=200,
        ),
    ]

    monkeypatch.setattr(
        "app.services.knowledge_base_service.crawl_site",
        lambda *args, **kwargs: pages,
    )
    monkeypatch.setattr(
        "app.services.langchain_service.LangChainService.create_embeddings",
        lambda self, documents, workspace_id, knowledge_base_id=None: [],
    )

    resp = await auth_client.post(
        f"/api/v1/knowledge-base/crawl?workspace_id={ws_id}",
        json={
            "base_url": "https://example.com",
            "max_pages": 10,
            "max_depth": 2,
            "include_paths": [],
            "exclude_paths": [],
        },
    )

    assert resp.status_code == 202, resp.text
    job = resp.json()["job"]
    assert job["status"] == "pending"

    jobs_resp = await auth_client.get(
        f"/api/v1/knowledge-base/crawl/jobs?workspace_id={ws_id}"
    )
    assert jobs_resp.status_code == 200, jobs_resp.text
    jobs = jobs_resp.json()["jobs"]
    assert jobs[0]["status"] == "completed"
    assert jobs[0]["processed_items"] == 2

    links_resp = await auth_client.get(f"/api/v1/knowledge-base/links?workspace_id={ws_id}")
    assert links_resp.status_code == 200, links_resp.text
    links = links_resp.json()["links"]
    assert len(links) == 2
    assert {link["name"] for link in links} == {"Home", "Pricing"}
    assert all(link["status"] == "indexed" for link in links)
    assert links[0]["metadata"]["source_type"] == "crawler"

    assert await KnowledgeBase.find().count() == 2
