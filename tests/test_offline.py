import json
from pathlib import Path

import pytest

from aspire_mcp import offline

ROOT = Path(__file__).resolve().parent.parent
pytestmark = pytest.mark.skipif(not (ROOT / "Vectric Files").exists(), reason="sample data absent")


def test_product_info():
    assert offline.product_info()["product_name"] == "Aspire"


def test_postprocessors():
    names = offline.list_postprocessors()
    assert "ShopBot_Arc_Inch.pp" in names
    assert offline.read_postprocessor("ShopBot_Arc_Inch.pp")


def test_path_traversal_blocked():
    with pytest.raises(ValueError):
        offline.read_postprocessor("../../tools.tool_db")


def test_defaults_fonts_clipart():
    assert "ProfileMachine" in offline.list_toolpath_defaults()
    assert any("Helvetica" in f for f in offline.list_fonts())
    assert offline.list_clipart("Animals", 5)


def test_api_catalog():
    assert any(h["class"] == "ToolpathManager" for h in offline.search_lua_api("CreateProfilingToolpath"))
    assert json.loads((ROOT / "aspire_mcp/data/lua_api_catalog.json").read_text())["classes"]
