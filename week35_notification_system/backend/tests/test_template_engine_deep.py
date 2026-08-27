import pytest
from app.services.template_engine import TemplateEngine

def test_template_engine_basic_render():
    res = TemplateEngine.render("Hello {{ name }}!", {"name": "Alice"})
    assert res == "Hello Alice!"

def test_template_engine_multiple_variables():
    res = TemplateEngine.render("User {{ username }} logged in from {{ ip }}.", {"username": "vee", "ip": "127.0.0.1"})
    assert res == "User vee logged in from 127.0.0.1."

def test_template_engine_empty_template_string():
    assert TemplateEngine.render("", {"a": "b"}) == ""
    assert TemplateEngine.render(None, {"a": "b"}) == ""

def test_template_engine_none_variables():
    assert TemplateEngine.render("Static text", None) == "Static text"

def test_template_engine_missing_variable_handling():
    res = TemplateEngine.render("Hello {{ name }}, code is {{ code }}!", {"name": "Bob"})
    # Undefined variable renders empty or raw in fallback
    assert "Bob" in res

def test_template_engine_numeric_and_boolean_variables():
    res = TemplateEngine.render("Count: {{ count }}, Active: {{ active }}", {"count": 42, "active": True})
    assert res == "Count: 42, Active: True"

def test_template_engine_extract_single_variable():
    vars_found = TemplateEngine.extract_variables("Hello {{ name }}!")
    assert vars_found == ["name"]

def test_template_engine_extract_multiple_variables():
    vars_found = TemplateEngine.extract_variables("Hi {{ first_name }} {{ last_name }}, your ID is {{ user_id }}.")
    assert set(vars_found) == {"first_name", "last_name", "user_id"}

def test_template_engine_extract_no_variables():
    assert TemplateEngine.extract_variables("Static text with no variables.") == []

def test_template_engine_extract_empty_string():
    assert TemplateEngine.extract_variables("") == []
