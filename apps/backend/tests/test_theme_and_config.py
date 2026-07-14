"""Theme + AdvancedConfig update flows (the settings pages)."""


async def _make_workspace(auth_client, name="WS"):
    resp = await auth_client.post("/api/v1/workspaces/", json={"name": name})
    assert resp.status_code == 200, resp.text
    return resp.json()["_id"]


async def test_update_theme(auth_client):
    ws_id = await _make_workspace(auth_client)

    resp = await auth_client.put(
        f"/api/v1/theme/?workspace_id={ws_id}",
        json={"theme": "dark", "primary_color": "#000000"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["theme"] == "dark"

    # Persisted
    resp = await auth_client.get(f"/api/v1/theme/?workspace_id={ws_id}")
    assert resp.json()["theme"] == "dark"
    assert resp.json()["primary_color"] == "#000000"
    # Untouched fields keep defaults
    assert resp.json()["position"] == "bottom-right"


async def test_update_advanced_config_camel_case(auth_client):
    """The frontend sends camelCase keys; the API must map them."""
    ws_id = await _make_workspace(auth_client)

    resp = await auth_client.put(
        f"/api/v1/advanced-config/?workspace_id={ws_id}",
        json={"advanced_config": {"chunkSize": 512, "llmModel": "gpt-4o", "temperature": 0.7}},
    )
    assert resp.status_code == 200, resp.text

    resp = await auth_client.get(f"/api/v1/advanced-config/?workspace_id={ws_id}")
    config = resp.json()["advanced_config"]
    assert config["chunk_size"] == 512
    assert config["llm_model"] == "gpt-4o"
    assert abs(config["temperature"] - 0.7) < 1e-9
