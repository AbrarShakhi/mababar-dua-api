import pytest
from httpx import ASGITransport, AsyncClient

from mababar_dua_api import MaBabarDuaApi


@pytest.mark.asyncio
async def test_global_middleware_runs_for_every_route():
    log = []
    api = MaBabarDuaApi(middlewares=[lambda req: log.append("global")])

    @api.get("/a")
    def route_a(req, res):
        res.send("a")

    @api.get("/b")
    def route_b(req, res):
        res.send("b")

    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        await c.get("/a")
        await c.get("/b")

    assert log == ["global", "global"]


@pytest.mark.asyncio
async def test_route_specific_middleware_only_runs_for_its_route():
    log = []

    def mw_a(req):
        log.append("mw_a")

    api = MaBabarDuaApi()

    @api.get("/a", middlewares=[mw_a])
    def route_a(req, res):
        res.send("a")

    @api.get("/b")
    def route_b(req, res):
        res.send("b")

    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        await c.get("/a")
        await c.get("/b")

    assert log == ["mw_a"]


@pytest.mark.asyncio
async def test_async_middleware_supported():
    log = []

    async def async_mw(req):
        log.append("async_mw")

    api = MaBabarDuaApi(middlewares=[async_mw])

    @api.get("/ping")
    def ping(req, res):
        res.send("pong")

    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        await c.get("/ping")

    assert log == ["async_mw"]


@pytest.mark.asyncio
async def test_middleware_can_mutate_request():
    api = MaBabarDuaApi(middlewares=[lambda req: req.queries.update({"injected": "yes"})])

    @api.get("/check")
    def check(req, res):
        res.send(req.queries.get("injected", "no"))

    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        r = await c.get("/check")

    assert r.text == "yes"


@pytest.mark.asyncio
async def test_non_callable_middleware_raises():
    from mababar_dua_api.middleware import run_middlewares
    from mababar_dua_api.request import Request

    async def fake_receive():
        return {"type": "http.request", "body": b"", "more_body": False}

    scope = {
        "type": "http",
        "method": "GET",
        "path": "/",
        "query_string": b"",
        "headers": [],
    }
    req = Request(scope, fake_receive)

    with pytest.raises(ValueError):
        await run_middlewares(["not_a_callable"], req)


@pytest.mark.asyncio
async def test_global_and_route_middlewares_both_run():
    log = []

    api = MaBabarDuaApi(middlewares=[lambda req: log.append("global")])

    @api.get("/x", middlewares=[lambda req: log.append("route")])
    def route_x(req, res):
        res.send("x")

    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        await c.get("/x")

    assert log == ["global", "route"]
