import pytest
from httpx import ASGITransport, AsyncClient

from mababar_dua_api import HTTPException, MaBabarDuaApi


def _make_app():
    api = MaBabarDuaApi()

    @api.get("/forbidden")
    def forbidden(req, res):
        raise HTTPException(403, "Forbidden")

    @api.get("/error")
    def error(req, res):
        raise RuntimeError("something exploded")

    @api.get("/ok")
    def ok(req, res):
        res.send("fine")

    return api


@pytest.mark.asyncio
async def test_http_exception_returns_correct_status():
    api = _make_app()
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        r = await c.get("/forbidden")
    assert r.status_code == 403
    assert "Forbidden" in r.text


@pytest.mark.asyncio
async def test_unknown_route_returns_404():
    api = _make_app()
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        r = await c.get("/doesnotexist")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_unhandled_exception_returns_500():
    api = _make_app()
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        r = await c.get("/error")
    assert r.status_code == 500
    assert "Internal Server Error" in r.text


@pytest.mark.asyncio
async def test_normal_route_unaffected():
    api = _make_app()
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        r = await c.get("/ok")
    assert r.status_code == 200
    assert r.text == "fine"


def test_http_exception_default_detail():
    exc = HTTPException(404)
    assert exc.status_code == 404
    assert exc.detail == "Not Found"


def test_http_exception_custom_detail():
    exc = HTTPException(403, "Access denied")
    assert exc.status_code == 403
    assert exc.detail == "Access denied"


def test_http_exception_unknown_code():
    exc = HTTPException(418)
    assert exc.status_code == 418
    assert exc.detail == "HTTP Error"
