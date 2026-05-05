"""
Example usage:
    uvicorn example.main:app --reload
"""
from mababar_dua_api import HTTPException, JSONResponse, MaBabarDuaApi


def log_requests(request):
    print(f"[{request.method}] {request.path}")

app = MaBabarDuaApi(middlewares=[log_requests])


def require_token(request):
    token = request.headers.get("authorization", "")
    if token != "Bearer secret":
        raise HTTPException(401, "Missing or invalid token")


@app.get("/")
def index(req, res):
    res.send("Welcome to MaBabarDuaApi!")


@app.get("/users/{id}")
def get_user(req, res, id):
    res.send(f"User ID: {id}")


@app.get("/status")
def status(req, res):
    res.json({"status": "ok", "framework": "mababar-dua-api"})


@app.post("/echo", middlewares=[require_token])
async def echo(req, res):
    body = await req.json()
    res.json(body, status_code=201)


@app.put("/users/{id}")
async def update_user(req, res, id):
    body = await req.json()
    res.json({"id": id, "updated": body})


@app.patch("/users/{id}")
async def partial_update(req, res, id):
    body = await req.json()
    res.json({"id": id, "patched": body})


@app.delete("/users/{id}")
def delete_user(req, res, id):
    res.send(f"Deleted user {id}")


# Handlers can also return a Response object directly
@app.get("/health")
def health(req, res):
    return JSONResponse({"healthy": True})


@app.route("/items")
class Items:
    def get(req, res):
        res.send("list of items")

    def post(req, res):
        res.send("item created", 201)
