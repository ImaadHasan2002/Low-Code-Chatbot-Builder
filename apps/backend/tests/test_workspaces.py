"""Workspace creation auto-provisions Theme + AdvancedConfig and links them."""


async def test_create_and_list_workspace(auth_client):
    resp = await auth_client.post("/api/v1/workspaces/", json={"name": "My Bot"})
    assert resp.status_code == 200, resp.text
    ws = resp.json()
    assert ws["name"] == "My Bot"
    assert ws["theme_config_id"] is not None
    assert ws["advanced_config_id"] is not None

    resp = await auth_client.get("/api/v1/workspaces/")
    assert resp.status_code == 200
    workspaces = resp.json()
    assert len(workspaces) == 1
    assert workspaces[0]["name"] == "My Bot"


async def test_get_single_workspace(auth_client):
    resp = await auth_client.post("/api/v1/workspaces/", json={"name": "WS2"})
    ws_id = resp.json()["_id"]

    resp = await auth_client.get(f"/api/v1/workspaces/{ws_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "WS2"


async def test_workspace_default_theme_and_config(auth_client):
    resp = await auth_client.post("/api/v1/workspaces/", json={"name": "WS3"})
    ws_id = resp.json()["_id"]

    # Theme endpoint returns the auto-created default theme
    resp = await auth_client.get(f"/api/v1/theme/?workspace_id={ws_id}")
    assert resp.status_code == 200, resp.text
    theme = resp.json()
    assert theme["theme"] == "light"
    assert theme["primary_color"] == "#3B82F6"

    # Advanced config endpoint returns the auto-created default config
    resp = await auth_client.get(f"/api/v1/advanced-config/?workspace_id={ws_id}")
    assert resp.status_code == 200, resp.text
    config = resp.json()["advanced_config"]
    assert config["llm_model"] == "gpt-4o-mini"
    assert config["chunk_size"] == 1000
