# MaBabarDuaApi

[![Tests](https://github.com/abrarshakhi/mababar-dua-api/actions/workflows/tests.yml/badge.svg)](https://github.com/abrarshakhi/mababar-dua-api/actions/workflows/tests.yml)
[![PyPI version](https://img.shields.io/pypi/v/mababar-dua-api)](https://pypi.org/project/mababar-dua-api/)
[![Python versions](https://img.shields.io/pypi/pyversions/mababar-dua-api)](https://pypi.org/project/mababar-dua-api/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ASGI Python web framework.

## Installation

```bash
pip install mababar-dua-api
```

To run a server you also need an ASGI server:

```bash
pip install "mababar-dua-api[dev]"   # installs uvicorn + test deps
```

## Quick Start

```python
from mababar_dua_api import MaBabarDuaApi, JSONResponse

app = MaBabarDuaApi()

@app.get("/")
def index(req, res):
    res.send("Hello, World!")

@app.get("/users/{id}")
def get_user(req, res, id):
    res.json({"id": id})

@app.post("/users")
async def create_user(req, res):
    body = await req.json()
    res.json(body, status_code=201)
```

Run with uvicorn:

```bash
uvicorn myapp:app --reload
```

## Features

- **Async-first** — built on the ASGI protocol, compatible with uvicorn / hypercorn
- **Familiar decorator API** — `@app.get()`, `@app.post()`, `@app.put()`, `@app.patch()`, `@app.delete()`
- **Class-based views** — `@app.route()` scans a class for HTTP method handlers
- **Path parameters** — `/users/{id}`, `/items/{name}/{color}`
- **Query string parsing** — `req.queries["key"]`
- **Async body / JSON** — `await req.body()`, `await req.json()`
- **Response helpers** — `res.send()`, `res.json()`, `res.render()` (HTML templates)
- **Return-style responses** — handlers can return `JSONResponse(...)` or `HTMLResponse(...)`
- **Middleware** — global and per-route, sync or async
- **Exception handling** — `HTTPException(status_code, detail)`, automatic 404 and 500

## Routing

```python
@app.get("/items")
def list_items(req, res):
    res.send("all items")

@app.get("/items/{id}")
def get_item(req, res, id):
    res.json({"id": id})

# Class-based view
@app.route("/orders")
class Orders:
    def get(req, res):
        res.send("list orders")

    def post(req, res):
        res.send("create order", 201)
```

## Middleware

```python
def log(req):
    print(f"[{req.method}] {req.path}")

async def auth(req):
    if not req.headers.get("authorization"):
        from mababar_dua_api import HTTPException
        raise HTTPException(401)

# Global middleware runs on every request
app = MaBabarDuaApi(middlewares=[log])

# Per-route middleware
@app.get("/secret", middlewares=[auth])
def secret(req, res):
    res.send("shh")
```

## Request

| Attribute / Method | Description |
|---|---|
| `req.method` | HTTP method (`"GET"`, `"POST"`, …) |
| `req.path` | URL path (`"/users/42"`) |
| `req.queries` | Parsed query string dict |
| `req.headers` | Lowercase header dict |
| `req.path_params` | Path parameter dict set by router |
| `await req.body()` | Raw request body as `bytes` |
| `await req.json()` | JSON-decoded request body |
| `await req.text()` | Body decoded as UTF-8 string |

## Response

| Method | Description |
|---|---|
| `res.send(text, status_code=200)` | Plain text response |
| `res.json(data, status_code=200)` | JSON response |
| `res.render(template_name, context)` | Render `<name>.html` template |
| `return JSONResponse(data)` | Return-style JSON response |
| `return HTMLResponse(html)` | Return-style HTML response |

## Development

```bash
# clone and install in editable mode
pip install -e ".[dev]"

# run tests
pytest -v

# run the example app
uvicorn example.main:app --reload
```

## License

MIT

