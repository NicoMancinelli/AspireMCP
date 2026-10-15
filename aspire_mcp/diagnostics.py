"""Builds a paste-able feedback report. Contains no secrets: only paths, versions, check results."""
from __future__ import annotations

import platform
import sys
from importlib import metadata

from . import offline


def _count(fn) -> str:
    try:
        return str(len(fn()))
    except Exception as e:  # report, don't fail
        return f"ERROR {e!r}"


def build_report(bridge_info: dict, last_lua: dict | None = None) -> str:
    try:
        ver = metadata.version("aspire-mcp")
    except metadata.PackageNotFoundError:
        ver = "dev"
    lines = [
        "# Aspire MCP feedback report",
        f"- aspire-mcp: {ver} (STATUS: in development)",
        f"- OS: {platform.platform()} | Python {sys.version.split()[0]}",
        f"- product_info: {offline.product_info() or 'NOT FOUND'}",
        f"- data_dir: {offline.data_dir()} (exists={offline.data_dir().is_dir()})",
        f"- install_dir: {offline.install_dir()} (exists={offline.install_dir().is_dir()})",
        f"- postprocessors: {_count(offline.list_postprocessors)}",
        f"- toolpath defaults: {_count(offline.list_toolpath_defaults)}",
        f"- fonts: {_count(offline.list_fonts)}",
        f"- clipart: {_count(lambda: offline.list_clipart(limit=100000))}",
        f"- bridge: {bridge_info}",
    ]
    if last_lua is not None:
        lines.append(f"- last Lua probe: {last_lua}")
    lines += ["", "## What the user should add",
              "- What they asked the AI to do, what happened, exact error text.",
              "- Aspire version/edition and where gadgets are installed."]
    return "\n".join(lines)
