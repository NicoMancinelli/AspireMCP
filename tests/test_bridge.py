import asyncio

from aspire_mcp.bridge import Bridge


async def _fake_gadget(port, reply=b"42"):
    r, w = await asyncio.open_connection("127.0.0.1", port)
    n = int((await r.readline()).decode())
    code = await r.readexactly(n)
    w.write(b"OK %d\n" % len(reply) + reply)
    await w.drain()
    return code, w


def test_roundtrip():
    async def go():
        b = Bridge(port=0)
        await b.start()
        port = b._server.sockets[0].getsockname()[1]
        ok0, msg = await b.run_lua("return 1")
        assert not ok0 and "not connected" in msg
        g = asyncio.create_task(_fake_gadget(port))
        await asyncio.wait_for(b._connected.wait(), 2)
        ok, out = await b.run_lua("return 6*7")
        code, w = await g
        assert (ok, out, code) == (True, "42", b"return 6*7")
        w.close()
        b._server.close()
    asyncio.run(go())


def test_port_in_use_is_reported():
    async def go():
        a = Bridge(port=0)
        await a.start()
        port = a._server.sockets[0].getsockname()[1]
        b = Bridge(port=port)
        await b.start()
        ok, msg = await b.run_lua("return 1")
        assert not ok and "cannot listen" in msg
        a._server.close()
    asyncio.run(go())
