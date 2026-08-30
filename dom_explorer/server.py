"""DOM Explorer MCP Server.
Provides interactive DOM exploration, element inspection, and Robot Framework locator generation.
"""

from __future__ import annotations

import json
from typing import Any, Dict, List, Optional
from mcp.server.mcpserver import MCPServer

from dom_explorer.browser.session import BrowserSessionManager
from dom_explorer.templates.robot_resource import RobotResourceTemplate

server = MCPServer(
    name="dom-explorer",
    instructions=(
        "DOM Explorer MCP Server para automação de testes com Robot Framework. "
        "Permite abrir páginas web, capturar elementos clicados pelo usuário em tempo real, "
        "escanear o DOM e gerar seletores e arquivos .resource para Browser Library e SeleniumLibrary."
    ),
)

# Global session instance
session = BrowserSessionManager()


@server.tool()
async def launch_browser(
    url: str,
    headless: bool = False,
    browser_type: str = "chromium",
) -> Dict[str, Any]:
    """Abre um navegador visível (headful por padrão) na URL informada e injeta o inspetor do DOM Explorer.

    Args:
        url: O endereço web para navegar (ex: 'https://exemplo.com.br' ou 'localhost:3000').
        headless: Se True, roda em segundo plano. Padrão False (abre janela visível para o usuário interagir).
        browser_type: Tipo de navegador ('chromium', 'firefox', 'webkit'). Padrão 'chromium'.
    """
    return await session.launch(url, headless=headless, browser_type=browser_type)


@server.tool()
async def get_selected_element() -> Dict[str, Any]:
    """Recupera o último elemento selecionado/clicado pelo usuário no navegador.
    Retorna metadados completos (tag, id, classes, atributos, texto), além de locators
    ranqueados para Robot Framework (Browser Library e SeleniumLibrary) e keywords prontas.
    """
    return await session.get_selected_element()


@server.tool()
async def get_selection_history() -> List[Dict[str, Any]]:
    """Retorna o histórico de todos os elementos selecionados/inspecionados na sessão atual."""
    return await session.get_selection_history()


@server.tool()
async def scan_elements(
    selector: Optional[str] = None,
    tag: Optional[str] = None,
    role: Optional[str] = None,
    text: Optional[str] = None,
    limit: int = 25,
) -> List[Dict[str, Any]]:
    """Varre o DOM da página atual procurando elementos interativos por critérios textuais ou semânticos.
    Útil para mapear formulários ou botões sem necessidade de clicar em cada um manualmente.

    Args:
        selector: Seletor CSS específico para buscar (ex: 'form.login input').
        tag: Filtrar por tag HTML (ex: 'button', 'input', 'select', 'a').
        role: Filtrar por ARIA role (ex: 'button', 'checkbox', 'tab').
        text: Filtrar por texto visível parcial (case-insensitive, ex: 'Salvar' ou 'Entrar').
        limit: Quantidade máxima de elementos a retornar (padrão 25).
    """
    return await session.scan_elements(
        selector=selector,
        tag=tag,
        role=role,
        text=text,
        limit=limit,
    )


@server.tool()
async def highlight_element(selector: str) -> Dict[str, Any]:
    """Destaca visualmente um elemento na página do navegador através de um seletor e valida se ele é único.

    Args:
        selector: Seletor CSS ou ID a validar e destacar (ex: '#login-btn' ou '[data-testid=\"submit\"]').
    """
    return await session.highlight_element(selector)


@server.tool()
async def export_robot_resource(
    page_name: str,
    library: str = "Browser",
) -> str:
    """Gera um arquivo de recurso (.resource) completo para o Robot Framework baseado nos elementos
    inspecionados até o momento, contendo a seção *** Variables *** e *** Keywords *** (Page Object Pattern).

    Args:
        page_name: Nome da página ou componente (ex: 'LoginPage', 'DashboardHeader').
        library: Biblioteca alvo do Robot Framework ('Browser' para Playwright ou 'SeleniumLibrary').
    """
    history = await session.get_selection_history()
    elements = [item["element"] for item in history if "element" in item]
    if not elements:
        # Check if there is a currently selected element
        current = await session.get_selected_element()
        if current.get("has_selection") and "element" in current:
            elements = [current["element"]]

    return RobotResourceTemplate.generate(
        page_name=page_name,
        elements=elements,
        library=library,
    )


@server.tool()
async def close_browser() -> Dict[str, str]:
    """Encerra a sessão do navegador e limpa os recursos."""
    await session.close()
    return {"status": "closed", "message": "Navegador encerrado com sucesso."}


def main():
    """Inicia o servidor MCP com transporte stdio."""
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
