"""Tests for DOM Explorer MCP Server registration and tool schemas."""

import pytest
from dom_explorer.server import server


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
