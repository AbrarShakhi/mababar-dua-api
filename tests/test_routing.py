import pytest
from httpx import ASGITransport, AsyncClient

from mababar_dua_api import MaBabarDuaApi


@pytest.fixture
def app():
    api = MaBabarDuaApi()

    @api.get("/hello")
    def get_hello(req, res):
        res.send("hello get")

    @api.post("/hello")
    def post_hello(req, res):
        res.send("hello post", 201)

    @api.put("/hello")
    def put_hello(req, res):
        res.send("hello put")

    @api.patch("/hello")
    def patch_hello(req, res):
        res.send("hello patch")

    @api.delete("/hello")
    def delete_hello(req, res):
        res.send("hello delete")

    @api.get("/users/{id}")
    def get_user(req, res, id):
        res.send(f"user:{id}")

    @api.get("/items/{name}/{color}")
    def get_item(req, res, name, color):
        res.send(f"{name}-{color}")

    return api


async def _client(app):
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")


@pytest.mark.asyncio
async def test_get(app):
    async with await _client(app) as c:
        r = await c.get("/hello")
    assert r.status_code == 200
    assert r.text == "hello get"


@pytest.mark.asyncio
async def test_post(app):
    async with await _client(app) as c:
        r = await c.post("/hello")
    assert r.status_code == 201
    assert r.text == "hello post"


@pytest.mark.asyncio
async def test_put(app):
    async with await _client(app) as c:
        r = await c.put("/hello")
    assert r.status_code == 200
    assert r.text == "hello put"


@pytest.mark.asyncio
async def test_patch(app):
    async with await _client(app) as c:
        r = await c.patch("/hello")
    assert r.status_code == 200
    assert r.text == "hello patch"


@pytest.mark.asyncio
async def test_delete(app):
    async with await _client(app) as c:
        r = await c.delete("/hello")
    assert r.status_code == 200
    assert r.text == "hello delete"


@pytest.mark.asyncio
async def test_path_param_single(app):
    async with await _client(app) as c:
        r = await c.get("/users/42")
    assert r.status_code == 200
    assert r.text == "user:42"


@pytest.mark.asyncio
async def test_path_param_multiple(app):
    async with await _client(app) as c:
        r = await c.get("/items/widget/blue")
    assert r.status_code == 200
    assert r.text == "widget-blue"


@pytest.mark.asyncio
async def test_unknown_path_returns_404(app):
    async with await _client(app) as c:
        r = await c.get("/notfound")
    assert r.status_code == 404


@pytest.mark.asyncio
async def test_default_path_uses_function_name():
    api = MaBabarDuaApi()

    @api.get()
    def myhandler(req, res):
        res.send("ok")

    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        r = await c.get("/myhandler")
    assert r.status_code == 200
    assert r.text == "ok"


@pytest.mark.asyncio
async def test_class_based_view():
    api = MaBabarDuaApi()

    @api.route("/things")
    class Things:
        def get(req, res):
            res.send("things get")

        def post(req, res):
            res.send("things post", 201)

        def helper():
            pass

    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        rg = await c.get("/things")
        rp = await c.post("/things")

    assert rg.status_code == 200
    assert rg.text == "things get"
    assert rp.status_code == 201
    assert rp.text == "things post"


@pytest.mark.asyncio
async def test_async_handler():
    api = MaBabarDuaApi()

    @api.get("/async")
    async def async_handler(req, res):
        res.send("async ok")

    async with AsyncClient(transport=ASGITransport(app=api), base_url="http://test") as c:
        r = await c.get("/async")
    assert r.status_code == 200
    assert r.text == "async ok"


@pytest.mark.asyncio
async def test_route_decorator_raises_on_non_class():
    api = MaBabarDuaApi()
    with pytest.raises(ValueError):
        @api.route("/bad")
        def not_a_class(req, res):
            pass
