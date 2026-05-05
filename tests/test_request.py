import json

import pytest
from httpx import ASGITransport, AsyncClient

from mababar_dua_api import MaBabarDuaApi


def _make_app():
    api = MaBabarDuaApi()

    @api.get("/qs")
    async def query_handler(req, res):
        res.send(json.dumps(dict(req.queries)))

    @api.post("/body")
    async def body_handler(req, res):
        data = await req.json()
        res.send(json.dumps(data), 200)

    @api.get("/headers")
    async def header_handler(req, res):
        ua = req.headers.get("x-custom-header", "")
        res.send(ua)

    @api.get("/text")
    async def text_handler(req, res):
        res.send(req.method)

    return api


@pytest.mark.asyncio
async def test_single_query_param():
    api = _make_app()
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        r = await c.get("/qs?name=Alice")
    assert r.status_code == 200
    assert json.loads(r.text) == {"name": "Alice"}


@pytest.mark.asyncio
async def test_multiple_query_params():
    api = _make_app()
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        r = await c.get("/qs?name=Alice&age=30")
    data = json.loads(r.text)
    assert data["name"] == "Alice"
    assert data["age"] == "30"


@pytest.mark.asyncio
async def test_empty_query_string():
    api = _make_app()
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        r = await c.get("/qs")
    assert json.loads(r.text) == {}


@pytest.mark.asyncio
async def test_json_body():
    api = _make_app()
    payload = {"user": "Bob", "score": 99}
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        r = await c.post("/body", json=payload)
    assert r.status_code == 200
    assert json.loads(r.text) == payload


@pytest.mark.asyncio
async def test_custom_header():
    api = _make_app()
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        r = await c.get("/headers", headers={"x-custom-header": "myvalue"})
    assert r.text == "myvalue"


@pytest.mark.asyncio
async def test_method_attribute():
    api = _make_app()
    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        r = await c.get("/text")
    assert r.text == "GET"
