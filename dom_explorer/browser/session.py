"""Playwright browser session manager for DOM Explorer."""

from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, List, Optional

from playwright.async_api import Browser, BrowserContext, Page, async_playwright

from dom_explorer.locators.robot_generator import RobotLocatorGenerator

INSPECTOR_SCRIPT_PATH = Path(__file__).parent / "inspector_script.js"


class BrowserSessionManager:
    """Manages headful/headless Playwright browser sessions and page inspections."""

    def __init__(self) -> None:
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        self._headless: Optional[bool] = None
        self._browser_type: Optional[str] = None
        self._inspector_script: str = ""
        self._load_inspector_script()

    def _load_inspector_script(self) -> None:
        if INSPECTOR_SCRIPT_PATH.exists():
            self._inspector_script = INSPECTOR_SCRIPT_PATH.read_text(encoding="utf-8")
        else:
            self._inspector_script = ""

    async def ensure_active_page(self) -> Page:
        if not self._page or self._page.is_closed():
            raise RuntimeError("Nenhuma sessão de navegador ativa. Chame 'launch_browser' primeiro.")
        return self._page

    async def launch(
        self,
        url: str,
        headless: bool = False,
        browser_type: str = "chromium",
    ) -> Dict[str, Any]:
        """Launches a browser session, navigates to the URL, and injects the DOM inspector."""
        if browser_type not in {"chromium", "firefox", "webkit"}:
            raise ValueError(
                "browser_type deve ser um de: chromium, firefox, webkit"
            )
        if not url.strip():
            raise ValueError("url não pode ser vazia")

        if not url.startswith(("http://", "https://", "file://")):
            url = f"https://{url}"

        # Reuse only when the requested browser configuration is unchanged.
        if self._page and not self._page.is_closed():
            if self._headless == headless and self._browser_type == browser_type:
                await self._page.goto(url, wait_until="domcontentloaded", timeout=45000)
                if self._inspector_script:
                    await self._page.evaluate(self._inspector_script)
                title = await self._page.title()
                return {
                    "status": "reused",
                    "url": self._page.url,
                    "title": title,
                    "message": f"Navegado com sucesso para {self._page.url} na janela existente.",
                }
            await self.close()
        elif self._browser or self._context or self._playwright:
            await self.close()

        self._playwright = await async_playwright().start()
        launcher = getattr(self._playwright, browser_type, self._playwright.chromium)

        launch_args = ["--start-maximized"] if not headless else []
        self._browser = await launcher.launch(
            headless=headless,
            args=launch_args,
        )

        self._context = await self._browser.new_context(
            no_viewport=True if not headless else False,
        )

        # Inject inspector on all future page loads / navigations
        if self._inspector_script:
            await self._context.add_init_script(self._inspector_script)

        self._page = await self._context.new_page()
        self._headless = headless
        self._browser_type = browser_type
        await self._page.goto(url, wait_until="domcontentloaded", timeout=45000)

        # Ensure inspector script is executed on the page immediately
        if self._inspector_script:
            await self._page.evaluate(self._inspector_script)

        title = await self._page.title()
        return {
            "status": "launched",
            "url": self._page.url,
            "title": title,
            "headless": headless,
            "message": (
                f"Navegador aberto com sucesso em {self._page.url}. "
                "O inspetor interativo está ativo. O usuário pode clicar em elementos para selecioná-los."
            ),
        }

    async def get_selected_element(self) -> Dict[str, Any]:
        """Retrieves the last element selected by the user, augmented with Robot Framework locators."""
        page = await self.ensure_active_page()

        selection = await page.evaluate("() => window.__domExplorerSelection || null")
        if not selection:
            return {
                "has_selection": False,
                "message": "Nenhum elemento selecionado ainda. Clique em um elemento no navegador para inspecioná-lo.",
            }

        # Calculate Robot Framework locators and snippets
        locators_info = RobotLocatorGenerator.generate_locators(selection)
        keywords_browser = RobotLocatorGenerator.generate_keywords(
            selection, locators_info["variable_name"], library="Browser"
        )
        keywords_selenium = RobotLocatorGenerator.generate_keywords(
            selection, locators_info["variable_name"], library="SeleniumLibrary"
        )

        return {
            "has_selection": True,
            "element": selection,
            "robot_locators": locators_info,
            "robot_keywords": {
                "browser_library": keywords_browser,
                "selenium_library": keywords_selenium,
            },
        }

    async def get_selection_history(self) -> List[Dict[str, Any]]:
        """Retrieves history of inspected elements during the current session."""
        page = await self.ensure_active_page()
        history = await page.evaluate("() => window.__domExplorerHistory || []")

        augmented_history = []
        for item in history:
            locators = RobotLocatorGenerator.generate_locators(item)
            augmented_history.append({
                "element": item,
                "variable_name": locators["variable_name"],
                "best_browser_locator": locators["browser_library"]["best"],
                "best_selenium_locator": locators["selenium_library"]["best"],
            })
        return augmented_history

    async def get_selected_component_elements(
        self,
        only_interactive: bool = True,
        max_depth: int = 3,
    ) -> List[Dict[str, Any]]:
        """Returns the selected element and matching descendants up to max_depth."""
        if max_depth < 0:
            raise ValueError("max_depth não pode ser negativo")

        page = await self.ensure_active_page()
        return await page.evaluate(
            """
            ({ onlyInteractive, maxDepth }) => {
                const root = window.__domExplorerSelectedElement;
                const extract = window.__domExplorerExtractElementMetadata;
                if (!root || typeof extract !== 'function') return [];

                const interactiveTags = new Set(['button', 'input', 'select', 'textarea', 'a']);
                const elements = [];
                const visit = (element, depth) => {
                    const metadata = extract(element);
                    const isInteractive = interactiveTags.has(metadata.tag) || Boolean(metadata.role);
                    if (depth === 0 || !onlyInteractive || (isInteractive && metadata.isInteractable)) {
                        elements.push(metadata);
                    }
                    if (depth >= maxDepth) return;
                    for (const child of element.children) visit(child, depth + 1);
                };

                visit(root, 0);
                return elements;
            }
            """,
            {"onlyInteractive": only_interactive, "maxDepth": max_depth},
        )

    async def highlight_element(self, selector: str) -> Dict[str, Any]:
        """Visually highlights an element using a CSS selector or ID and validates uniqueness."""
        page = await self.ensure_active_page()

        # Clean selector if robot prefix was included
        clean_selector = selector
        if clean_selector.startswith("css="):
            clean_selector = clean_selector[4:]
        elif clean_selector.startswith("id="):
            clean_selector = f"#{clean_selector[3:]}"
        elif clean_selector.startswith("id:"):
            clean_selector = f"#{clean_selector[3:]}"
        elif clean_selector.startswith("css:"):
            clean_selector = clean_selector[4:]

        script = """
        (sel) => {
            try {
                const els = document.querySelectorAll(sel);
                let highlighted = false;
                if (els.length > 0 && typeof window.__domExplorerHighlight === 'function') {
                    highlighted = window.__domExplorerHighlight(sel);
                }
                return {
                    count: els.length,
                    is_unique: els.length === 1,
                    highlighted: highlighted
                };
            } catch (err) {
                return {
                    count: 0,
                    is_unique: false,
                    highlighted: false,
                    error: err.message
                };
            }
        }
        """
        result = await page.evaluate(script, clean_selector)
        return {
            "selector": selector,
            "clean_selector": clean_selector,
            "match_count": result.get("count", 0),
            "is_unique": result.get("is_unique", False),
            "highlighted": result.get("highlighted", False),
            "error": result.get("error"),
        }

    async def scan_elements(
        self,
        selector: Optional[str] = None,
        tag: Optional[str] = None,
        role: Optional[str] = None,
        text: Optional[str] = None,
        limit: int = 25,
    ) -> List[Dict[str, Any]]:
        """Scans the DOM for elements matching textual or semantic criteria."""
        if limit < 1:
            raise ValueError("limit deve ser maior que zero")

        page = await self.ensure_active_page()

        scan_script = """
        (criteria) => {
            const results = [];
            let candidateElements = [];

            if (criteria.selector) {
                try {
                    candidateElements = Array.from(document.querySelectorAll(criteria.selector));
                } catch(e) {
                    return { error: e.message, items: [] };
                }
            } else if (criteria.tag) {
                candidateElements = Array.from(document.getElementsByTagName(criteria.tag));
            } else {
                // Default interactive elements
                candidateElements = Array.from(document.querySelectorAll(
                    'button, input, select, textarea, a[href], [role="button"], [role="link"], [role="checkbox"], [role="radio"], [role="tab"], [role="menuitem"]'
                ));
            }

            for (const el of candidateElements) {
                if (results.length >= criteria.limit) break;

                // Check visibility
                const isVisible = el.offsetWidth > 0 && el.offsetHeight > 0;
                if (!isVisible) continue;

                // Filter by role if specified
                if (criteria.role) {
                    const elRole = el.getAttribute('role') || '';
                    if (elRole.toLowerCase() !== criteria.role.toLowerCase()) continue;
                }

                // Filter by text if specified
                const elText = (el.innerText || el.textContent || '').trim();
                if (criteria.text) {
                    if (!elText.toLowerCase().includes(criteria.text.toLowerCase())) continue;
                }

                const rect = el.getBoundingClientRect();
                const tag = el.tagName.toLowerCase();
                const id = el.id || '';
                const name = el.getAttribute('name') || '';
                const type = el.getAttribute('type') || (tag === 'input' ? 'text' : '');
                const placeholder = el.getAttribute('placeholder') || '';
                const role = el.getAttribute('role') || '';
                const ariaLabel = el.getAttribute('aria-label') || '';
                const testIdAttributes = ['data-testid', 'data-test', 'data-cy', 'data-qa'];
                const testIdAttribute = testIdAttributes.find((attribute) => el.hasAttribute(attribute)) || '';
                const testId = testIdAttribute ? el.getAttribute(testIdAttribute) : '';

                results.push({
                    tag,
                    id,
                    name,
                    type,
                    placeholder,
                    role,
                    ariaLabel,
                    testId,
                    testIdAttribute,
                    text: elText.slice(0, 100),
                    classList: Array.from(el.classList),
                    boundingBox: {
                        x: Math.round(rect.x),
                        y: Math.round(rect.y),
                        width: Math.round(rect.width),
                        height: Math.round(rect.height)
                    },
                    isInteractable: !el.disabled
                });
            }

            return { items: results };
        }
        """

        criteria = {
            "selector": selector,
            "tag": tag,
            "role": role,
            "text": text,
            "limit": limit,
        }

        eval_result = await page.evaluate(scan_script, criteria)
        if eval_result.get("error"):
            raise ValueError(f"Seletor CSS inválido: {eval_result['error']}")
        items = eval_result.get("items", [])

        augmented = []
        for item in items:
            locators_info = RobotLocatorGenerator.generate_locators(item)
            augmented.append({
                "tag": item["tag"],
                "id": item.get("id"),
                "text": item.get("text"),
                "name": item.get("name"),
                "testId": item.get("testId"),
                "testIdAttribute": item.get("testIdAttribute"),
                "variable_name": locators_info["variable_name"],
                "browser_locator": locators_info["browser_library"]["best"],
                "selenium_locator": locators_info["selenium_library"]["best"],
                "all_locators": locators_info,
            })

        return augmented

    async def close(self) -> None:
        """Closes all browser contexts and terminates the Playwright instance."""
        if self._page and not self._page.is_closed():
            try:
                await self._page.close()
            except Exception:
                pass
            self._page = None

        if self._context:
            try:
                await self._context.close()
            except Exception:
                pass
            self._context = None

        if self._browser:
            try:
                await self._browser.close()
            except Exception:
                pass
            self._browser = None

        if self._playwright:
            try:
                await self._playwright.stop()
            except Exception:
                pass
            self._playwright = None

        self._headless = None
        self._browser_type = None
