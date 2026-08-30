"""Integration tests for Playwright browser session and DOM Inspector."""

import tempfile
from pathlib import Path
import pytest
from dom_explorer.browser.session import BrowserSessionManager


@pytest.fixture
def sample_html_file():
    html_content = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <title>Página de Teste de Automação</title>
</head>
<body>
    <div class="container">
        <h1>Formulário de Acesso</h1>
        <form id="login-form">
            <label for="username">Nome de Usuário</label>
            <input type="text" id="username" name="user" placeholder="Digite seu usuário" />

            <label for="password">Senha</label>
            <input type="password" id="password" name="pwd" placeholder="Digite sua senha" />

            <button type="submit" id="btn-login" data-testid="login-submit-btn">Entrar no Sistema</button>
            <a href="#" id="link-forgot" role="link">Esqueci minha senha</a>
        </form>
    </div>
</body>
</html>
"""
    with tempfile.NamedTemporaryFile("w", suffix=".html", delete=False) as f:
        f.write(html_content)
        temp_path = f.name

    yield temp_path
    Path(temp_path).unlink(missing_ok=True)


@pytest.mark.asyncio
async def test_browser_session_lifecycle_and_inspection(sample_html_file):
    session = BrowserSessionManager()
    file_url = f"file://{sample_html_file}"

    # 1. Launch browser in headless mode for CI/test
    launch_result = await session.launch(file_url, headless=True)
    assert launch_result["status"] == "launched"
    assert "Página de Teste de Automação" in launch_result["title"]

    # 2. Test scan_elements (semantic and textual scan)
    scanned_items = await session.scan_elements()
    assert len(scanned_items) >= 4  # username, password, submit button, link

    tags = [item["tag"] for item in scanned_items]
    assert "input" in tags
    assert "button" in tags

    # Verify button locators
    button_item = next(item for item in scanned_items if item["tag"] == "button")
    assert button_item["testId"] == "login-submit-btn"
    assert button_item["browser_locator"] == '[data-testid="login-submit-btn"]'
    assert button_item["variable_name"] == "${BTN_ENTRAR_NO_SISTEMA}"

    # 3. Test highlight_element
    highlight_result = await session.highlight_element("#btn-login")
    assert highlight_result["is_unique"] is True
    assert highlight_result["match_count"] == 1

    # 4. Test simulated click / user selection
    page = await session.ensure_active_page()
    # Click the button (the inspector should intercept and record selection)
    await page.click("#btn-login")

    selection_data = await session.get_selected_element()
    assert selection_data["has_selection"] is True
    assert selection_data["element"]["id"] == "btn-login"
    assert selection_data["element"]["testId"] == "login-submit-btn"
    assert selection_data["robot_locators"]["variable_name"] == "${BTN_ENTRAR_NO_SISTEMA}"

    # Check generated keywords
    browser_kw = selection_data["robot_keywords"]["browser_library"]
    assert "Click Btn Entrar No Sistema" in browser_kw
    assert "Click    ${BTN_ENTRAR_NO_SISTEMA}" in browser_kw

    # 5. Test selection history
    history = await session.get_selection_history()
    assert len(history) >= 1
    assert history[0]["variable_name"] == "${BTN_ENTRAR_NO_SISTEMA}"

    # 6. Close session
    await session.close()
