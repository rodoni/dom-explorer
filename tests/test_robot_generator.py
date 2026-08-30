"""Unit tests for Robot Framework locator and code generator."""

import pytest
from dom_explorer.locators.robot_generator import (
    RobotLocatorGenerator,
    is_likely_dynamic_id,
    sanitize_variable_name,
)
from dom_explorer.templates.robot_resource import RobotResourceTemplate


def test_sanitize_variable_name():
    assert sanitize_variable_name("Entrar no Sistema") == "ENTRAR_NO_SISTEMA"
    assert sanitize_variable_name("Usuário & Senha!") == "USUARIO_SENHA"
    assert sanitize_variable_name("e-mail-address") == "E_MAIL_ADDRESS"
    assert sanitize_variable_name("") == "ELEMENT"


def test_is_likely_dynamic_id():
    # Dynamic patterns
    assert is_likely_dynamic_id(":r0:") is True
    assert is_likely_dynamic_id(":r1a:") is True
    assert is_likely_dynamic_id("123456") is True
    assert is_likely_dynamic_id("ext-gen-102") is True
    assert is_likely_dynamic_id("ember543") is True
    assert is_likely_dynamic_id("c1b2c3d4-e5f6-7a8b-9c0d-1e2f3a4b5c6d") is True

    # Stable patterns
    assert is_likely_dynamic_id("login-button") is False
    assert is_likely_dynamic_id("user_name") is False
    assert is_likely_dynamic_id("submitBtn") is False


def test_generate_variable_name_button():
    metadata = {
        "tag": "button",
        "type": "submit",
        "text": "Entrar no Sistema",
        "id": "btn-login",
    }
    var_name = RobotLocatorGenerator.generate_variable_name(metadata)
    assert var_name == "${BTN_ENTRAR_NO_SISTEMA}"


def test_generate_variable_name_input():
    metadata = {
        "tag": "input",
        "type": "text",
        "name": "username",
        "placeholder": "Digite seu e-mail",
    }
    var_name = RobotLocatorGenerator.generate_variable_name(metadata)
    assert var_name == "${INPUT_USERNAME}"


def test_generate_locators_with_test_id():
    metadata = {
        "tag": "button",
        "type": "button",
        "id": ":r0:",  # dynamic ID should be ignored as primary
        "testId": "confirm-checkout",
        "text": "Finalizar Pedido",
    }
    locators = RobotLocatorGenerator.generate_locators(metadata)
    browser_locs = locators["browser_library"]
    selenium_locs = locators["selenium_library"]

    assert browser_locs["best"] == '[data-testid="confirm-checkout"]'
    assert selenium_locs["best"] == 'css:[data-testid="confirm-checkout"]'


def test_generate_locators_with_stable_id():
    metadata = {
        "tag": "input",
        "type": "password",
        "id": "user-password",
        "name": "pwd",
        "placeholder": "Senha",
    }
    locators = RobotLocatorGenerator.generate_locators(metadata)
    browser_locs = locators["browser_library"]
    selenium_locs = locators["selenium_library"]

    assert browser_locs["best"] == "id=user-password"
    assert selenium_locs["best"] == "id:user-password"


def test_generate_keywords_browser_library():
    metadata = {
        "tag": "button",
        "type": "submit",
        "text": "Salvar",
    }
    kw = RobotLocatorGenerator.generate_keywords(metadata, "${BTN_SALVAR}", library="Browser")
    assert "Click Btn Salvar" in kw
    assert "Click    ${BTN_SALVAR}" in kw


def test_robot_resource_template_generation():
    elements = [
        {
            "tag": "input",
            "type": "text",
            "id": "login-user",
            "name": "user",
            "placeholder": "Usuário",
        },
        {
            "tag": "button",
            "type": "submit",
            "text": "Entrar",
            "id": "login-submit",
        },
    ]

    content = RobotResourceTemplate.generate("LoginPage", elements, library="Browser")
    assert "*** Settings ***" in content
    assert "Library          Browser" in content
    assert "*** Variables ***" in content
    assert "${INPUT_LOGIN_USER}" in content
    assert "id=login-user" in content
    assert "${BTN_ENTRAR}" in content
    assert "id=login-submit" in content
    assert "*** Keywords ***" in content
    assert "Fill Input Login User" in content
    assert "Click Btn Entrar" in content
