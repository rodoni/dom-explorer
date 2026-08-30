"""Template generator for Robot Framework .resource files (Page Object Pattern)."""

from __future__ import annotations

from typing import Any, Dict, List
from dom_explorer.locators.robot_generator import RobotLocatorGenerator


class RobotResourceTemplate:
    """Generates complete Robot Framework resource files."""

    @classmethod
    def generate(
        cls,
        page_name: str,
        elements: List[Dict[str, Any]],
        library: str = "Browser",
    ) -> str:
        """Generates a structured .resource file with Settings, Variables, and Keywords.

        Args:
            page_name: Name of the page or component (e.g. LoginPage, DashboardPage).
            elements: List of element metadata dictionaries.
            library: Target library, 'Browser' or 'SeleniumLibrary'.
        """
        if not page_name.strip():
            raise ValueError("page_name não pode ser vazio")
        if library not in {"Browser", "SeleniumLibrary"}:
            raise ValueError("library deve ser 'Browser' ou 'SeleniumLibrary'")

        clean_page_name = page_name.replace(" ", "")
        lib_name = library

        lines: List[str] = [
            "*** Settings ***",
            f"Documentation    Page Object Resource para {clean_page_name}",
            f"Library          {lib_name}",
            "",
            "*** Variables ***",
        ]

        seen_vars = set()
        variable_definitions = []
        keywords_code = []

        for elem in elements:
            locators_info = RobotLocatorGenerator.generate_locators(elem)
            var_name = locators_info["variable_name"]

            # Avoid duplicates by appending index if needed
            original_var = var_name
            counter = 1
            while var_name in seen_vars:
                var_name = f"{original_var[:-1]}_{counter}}}"
                counter += 1
            seen_vars.add(var_name)

            best_locator = (
                locators_info["browser_library"]["best"]
                if lib_name == "Browser"
                else locators_info["selenium_library"]["best"]
            )

            # Pad variable declaration nicely
            padding = " " * max(4, 36 - len(var_name))
            variable_definitions.append(f"{var_name}{padding}{best_locator}")

            # Generate keyword
            kw = RobotLocatorGenerator.generate_keywords(elem, var_name, library=lib_name)
            keywords_code.append(kw)

        if not variable_definitions:
            variable_definitions.append("# Nenhum elemento capturado ainda")

        lines.extend(variable_definitions)
        lines.append("")
        lines.append("*** Keywords ***")
        lines.append("")

        for kw in keywords_code:
            lines.append(kw)
            lines.append("")

        return "\n".join(lines)
