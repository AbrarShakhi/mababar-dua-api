import json
import os
import tempfile

import pytest
from httpx import ASGITransport, AsyncClient

from mababar_dua_api import HTMLResponse, JSONResponse, MaBabarDuaApi, Response


@pytest.mark.asyncio
async def test_response_send_text():
    api = MaBabarDuaApi()

    @api.get("/text")
    def route(req, res):
        res.send("hello world", 200)

    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        r = await c.get("/text")
    assert r.status_code == 200
    assert r.text == "hello world"


@pytest.mark.asyncio
async def test_response_custom_status_code():
    api = MaBabarDuaApi()

    @api.get("/created")
    def route(req, res):
        res.send("created", 201)

    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        r = await c.get("/created")
    assert r.status_code == 201
    assert r.text == "created"


@pytest.mark.asyncio
async def test_response_json_method():
    api = MaBabarDuaApi()

    @api.get("/data")
    def route(req, res):
        res.json({"msg": "ok", "count": 3})

    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        r = await c.get("/data")
    assert r.headers["content-type"] == "application/json"
    assert r.json() == {"msg": "ok", "count": 3}


@pytest.mark.asyncio
async def test_response_json_custom_status():
    api = MaBabarDuaApi()

    @api.post("/items")
    def route(req, res):
        res.json({"id": 1}, status_code=201)

    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        r = await c.post("/items")
    assert r.status_code == 201
    assert r.json() == {"id": 1}


@pytest.mark.asyncio
async def test_handler_returns_json_response():
    api = MaBabarDuaApi()

    @api.get("/health")
    def route(req, res):
        return JSONResponse({"healthy": True})

    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        r = await c.get("/health")
    assert r.status_code == 200
    assert r.json() == {"healthy": True}
    assert r.headers["content-type"] == "application/json"


@pytest.mark.asyncio
async def test_handler_returns_html_response():
    api = MaBabarDuaApi()

    @api.get("/page")
    def route(req, res):
        return HTMLResponse("<h1>Hello</h1>")

    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        r = await c.get("/page")
    assert r.status_code == 200
    assert "Hello" in r.text
    assert "text/html" in r.headers["content-type"]


@pytest.mark.asyncio
async def test_response_render_template():
    with tempfile.TemporaryDirectory() as tmpdir:
        tpl_path = os.path.join(tmpdir, "greeting.html")
        with open(tpl_path, "w") as f:
            f.write("<h1>Hello, {{ name }}!</h1><p>{{ msg }}</p>")

        api = MaBabarDuaApi()
        original_dir = os.getcwd()
        os.chdir(tmpdir)

        try:
            @api.get("/greet")
            def greet(req, res):
                res.render("greeting", {"name": "World", "msg": "Welcome"})

            async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
                r = await c.get("/greet")
        finally:
            os.chdir(original_dir)

    assert r.status_code == 200
    assert "Hello, World!" in r.text
    assert "Welcome" in r.text
    assert "text/html" in r.headers["content-type"]


def test_html_response_content_type():
    resp = HTMLResponse("<p>hi</p>", status_code=200)
    headers = dict(resp._build_headers())
    assert b"content-type" in headers
    assert b"text/html" in headers[b"content-type"]


def test_json_response_serialises_dict():
    resp = JSONResponse({"a": 1, "b": [1, 2]})
    assert json.loads(resp._content) == {"a": 1, "b": [1, 2]}
    headers = dict(resp._build_headers())
    assert headers[b"content-type"] == b"application/json"
