"""Offline (no Aspire required) readers for Vectric data files."""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

_HERE = Path(__file__).resolve().parent
_DEFAULT_ROOT = _HERE.parent / "Vectric Files"


def _first_existing(candidates: list[Path], fallback: Path) -> Path:
    return next((c for c in candidates if c.is_dir()), fallback)


def data_dir() -> Path:
    """Per-user data dir (PostP, ToolDatabase, Gadgets, ...). Override: ASPIRE_DATA_DIR."""
    if "ASPIRE_DATA_DIR" in os.environ:
        return Path(os.environ["ASPIRE_DATA_DIR"])
    pd = Path(os.environ.get("PROGRAMDATA", r"C:\ProgramData"))
    docs = Path(os.environ.get("PUBLIC", r"C:\Users\Public")) / "Documents"
    cands = [pd / "Vectric/Aspire/V8.5", docs / "Vectric/Aspire/V8.5", pd / "Vectric/Aspire"]
    return _first_existing(cands, _DEFAULT_ROOT / "Vectric/Aspire/V8.5")


def install_dir() -> Path:
    """Program install dir (Fonts, Clipart, ProductInfo.ini). Override: ASPIRE_INSTALL_DIR."""
    if "ASPIRE_INSTALL_DIR" in os.environ:
        return Path(os.environ["ASPIRE_INSTALL_DIR"])
    pf = Path(os.environ.get("PROGRAMFILES", r"C:\Program Files"))
    cands = [pf / "Aspire 8.5", pf / "Vectric/Aspire 8.5", pf / "Aspire"]
    return _first_existing(cands, _DEFAULT_ROOT / "Aspire 8.5")


def _safe_child(base: Path, name: str) -> Path:
    p = (base / name).resolve()
    if base.resolve() not in p.parents and p != base.resolve():
        raise ValueError(f"path escapes {base}: {name}")
    return p


def product_info() -> dict[str, str]:
    p = install_dir() / "ProductInfo.ini"
    out: dict[str, str] = {}
    if p.exists():
        for line in p.read_text(errors="replace").splitlines():
            k, sep, v = line.strip().partition("=")
            if sep:
                out[k] = v
    return out


def list_postprocessors() -> list[str]:
    d = data_dir()
    return sorted(p.name for sub in ("PostP", "My_PostP") for p in (d / sub).glob("*.pp"))


def read_postprocessor(name: str, max_bytes: int = 200_000) -> str:
    for sub in ("PostP", "My_PostP"):
        p = _safe_child(data_dir() / sub, name)
        if p.is_file():
            return p.read_bytes()[:max_bytes].decode("latin-1")
    raise FileNotFoundError(name)


def postprocessor_summary(name: str) -> dict[str, str]:
    """Pull the header fields (POST_NAME, FILE_EXTENSION, UNITS, ...)."""
    text = read_postprocessor(name)
    out: dict[str, str] = {}
    for key in ("POST_NAME", "FILE_EXTENSION", "UNITS", "DESCRIPTION", "ARC_SUPPORT"):
        m = re.search(rf'^\+?\s*{key}\s*=\s*"?([^"\r\n]*)"?', text, re.M)
        if m:
            out[key] = m.group(1).strip()
    return out


def list_toolpath_defaults() -> list[str]:
    return sorted(p.stem for p in (data_dir() / "ToolpathDefaults").glob("*.default"))


def list_fonts() -> list[str]:
    return sorted(p.stem for p in (install_dir() / "Fonts").glob("*.vfont"))


def list_clipart(category: str | None = None, limit: int = 200) -> list[str]:
    root = install_dir() / "Clipart"
    base = _safe_child(root, category) if category else root
    files = sorted(p.relative_to(root).as_posix() for p in base.rglob("*")
                   if p.suffix.lower() in {".v3m", ".crv", ".crv3d", ".art"})
    return files[:limit]


def list_tools_in_db(limit: int = 500) -> list[str]:
    """Best-effort: tool names are UTF-16LE/ASCII strings in the binary DB.

    The format is an MFC-style archive; this is a string scrape, not a parser.
    """
    p = data_dir() / "ToolDatabase" / "tools.tool_db"
    raw = p.read_bytes()
    names = {m.group(0).decode("ascii") for m in re.finditer(rb"#?[ -~]{6,}(?:\"[ -~]*)?", raw)
             if re.search(rb"(?i)(dia|ball|bit|end ?mill|v-?bit|deg)", m.group(0))}
    return sorted(names)[:limit]


def search_lua_api(query: str, limit: int = 50) -> list[dict]:
    cat = json.loads((_HERE / "data" / "lua_api_catalog.json").read_text())["classes"]
    q = query.lower()
    hits = []
    for cls, methods in sorted(cat.items()):
        ms = [m for m in methods if q in m.lower()]
        if q in cls.lower() or ms:
            hits.append({"class": cls, "methods": methods if q in cls.lower() else ms})
    return hits[:limit]
