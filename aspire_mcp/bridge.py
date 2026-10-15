"""TCP side of the bridge. The Aspire gadget connects to us (client role)."""
from __future__ import annotations

import asyncio


class Bridge:
    def __init__(self, host: str = "127.0.0.1", port: int = 8765):
        self.host, self.port = host, port
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._server: asyncio.base_events.Server | None = None
        self._lock = asyncio.Lock()
        self._connected = asyncio.Event()

    async def start(self) -> None:
        if self._server is None:
            self._server = await asyncio.start_server(self._on_conn, self.host, self.port)

    async def _on_conn(self, r: asyncio.StreamReader, w: asyncio.StreamWriter) -> None:
        if self._writer is not None:
            self._writer.close()
        self._reader, self._writer = r, w
        self._connected.set()

    @property
    def connected(self) -> bool:
        return self._writer is not None and not self._writer.is_closing()

    async def run_lua(self, code: str, timeout: float = 60.0) -> tuple[bool, str]:
        """Execute a Lua chunk in Aspire. Returns (ok, payload)."""
        await self.start()
        if not self.connected:
            return False, (f"Aspire gadget not connected. Run the 'MCP Bridge' gadget in Aspire "
                           f"(connects to {self.host}:{self.port}).")
        async with self._lock:
            assert self._reader and self._writer
            data = code.encode()
            try:
                self._writer.write(f"{len(data)}\n".encode() + data)
                await self._writer.drain()
                head = await asyncio.wait_for(self._reader.readline(), timeout)
                if not head:
                    self._writer = None
                    return False, "Aspire closed the connection."
                status, _, size = head.decode().strip().partition(" ")
                body = await asyncio.wait_for(self._reader.readexactly(int(size)), timeout)
            except (asyncio.TimeoutError, ConnectionError, asyncio.IncompleteReadError, ValueError) as e:
                self._writer = None
                return False, f"Bridge error: {e!r}"
            return status == "OK", body.decode(errors="replace")
