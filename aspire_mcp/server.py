"""Aspire MCP server (stdio)."""
from __future__ import annotations

import json

from mcp.server.fastmcp import FastMCP

from . import offline
from .bridge import Bridge

mcp = FastMCP("aspire")
bridge = Bridge()


def _lua_str(s: str) -> str:
    return json.dumps(s)  # JSON string literals are valid Lua 5.1 for our inputs (no \u escapes)


# ---- offline tools -------------------------------------------------------
@mcp.tool()
def product_info() -> dict:
    """Installed Aspire product name/version from ProductInfo.ini."""
    return offline.product_info()


@mcp.tool()
def list_postprocessors() -> list[str]:
    """List post processor (.pp) files."""
    return offline.list_postprocessors()


@mcp.tool()
def postprocessor_summary(name: str) -> dict:
    """Header fields (POST_NAME, FILE_EXTENSION, UNITS) of a post processor."""
    return offline.postprocessor_summary(name)


@mcp.tool()
def read_postprocessor(name: str) -> str:
    """Full text of a post processor file."""
    return offline.read_postprocessor(name)


@mcp.tool()
def list_toolpath_defaults() -> list[str]:
    """Toolpath default templates (Profile, Pocket, VCarve, ...)."""
    return offline.list_toolpath_defaults()


@mcp.tool()
def list_fonts() -> list[str]:
    """Installed .vfont fonts."""
    return offline.list_fonts()


@mcp.tool()
def list_clipart(category: str | None = None, limit: int = 200) -> list[str]:
    """Clipart files (relative paths), optionally within a category folder."""
    return offline.list_clipart(category, limit)


@mcp.tool()
def list_tool_database() -> list[str]:
    """Best-effort tool names scraped from tools.tool_db (not a full parser)."""
    return offline.list_tools_in_db()


@mcp.tool()
def search_lua_api(query: str) -> list[dict]:
    """Search the heuristic Lua API catalog (classes/methods recovered from Aspire.exe)."""
    return offline.search_lua_api(query)


# ---- live bridge ---------------------------------------------------------
@mcp.tool()
async def bridge_status() -> dict:
    """Whether the Aspire 'MCP Bridge' gadget is connected."""
    await bridge.start()
    return {"connected": bridge.connected, "host": bridge.host, "port": bridge.port}


@mcp.tool()
async def run_lua(code: str, timeout_s: float = 60.0) -> dict:
    """Execute a Lua chunk inside Aspire (via the bridge gadget). Use `return x` for output."""
    ok, out = await bridge.run_lua(code, timeout_s)
    return {"ok": ok, "output": out}


@mcp.tool()
async def get_job_info() -> dict:
    """[unverified] Basic info on the open job."""
    ok, out = await bridge.run_lua(
        'local job = VectricJob()\n'
        'if not job.Exists then return "no job" end\n'
        'return tostring(job.IsAspire)')
    return {"ok": ok, "output": out}


@mcp.tool()
async def import_vector_file(path: str) -> dict:
    """[unverified] Import a DXF/DWG into the open job."""
    ok, out = await bridge.run_lua(
        f'local job = VectricJob()\nlocal r = job:ImportDxfDwg({_lua_str(path)})\n'
        'job:Refresh2DView()\nreturn tostring(r)')
    return {"ok": ok, "output": out}


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
