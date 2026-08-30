"""Tests for DOM Explorer MCP Server registration and tool schemas."""

import pytest
from dom_explorer.server import export_robot_resource, server, session


@pytest.mark.asyncio
async def test_mcp_server_tools_registration():
    tools = await server.list_tools()
    tool_names = [tool.name for tool in tools]

    expected_tools = [
        "launch_browser",
        "get_selected_element",
        "get_selection_history",
        "scan_elements",
        "highlight_element",
        "export_robot_resource",
        "close_browser",
    ]

    for expected in expected_tools:
        assert expected in tool_names, f"Tool {expected} not registered in MCP Server"

    # Verify launch_browser parameters
    launch_tool = next(t for t in tools if t.name == "launch_browser")
    props = launch_tool.input_schema.get("properties", {})
    assert "url" in props
    assert "headless" in props
    assert "browser_type" in props
    assert launch_tool.input_schema["properties"]["browser_type"]["enum"] == [
        "chromium",
        "firefox",
        "webkit",
    ]

    export_tool = next(t for t in tools if t.name == "export_robot_resource")
    assert export_tool.input_schema["properties"]["library"]["enum"] == [
        "Browser",
        "SeleniumLibrary",
    ]
    assert export_tool.input_schema["properties"]["include_children"]["default"] is False
    assert export_tool.input_schema["properties"]["only_interactive"]["default"] is True
    assert export_tool.input_schema["properties"]["max_depth"]["default"] == 3
    assert export_tool.input_schema["properties"]["output_path"]["default"] is None


@pytest.mark.asyncio
async def test_export_robot_resource_writes_file(tmp_path, monkeypatch):
    async def selection_history():
        return [{
            "element": {
                "tag": "button",
                "type": "button",
                "text": "Salvar",
                "id": "save-button",
            }
        }]

    monkeypatch.setattr(session, "get_selection_history", selection_history)
    output_path = tmp_path / "resources" / "SavePage.resource"

    content = await export_robot_resource(
        page_name="SavePage",
        output_path=str(output_path),
    )

    assert output_path.read_text(encoding="utf-8") == content
    assert "${BTN_SALVAR}" in content
