from typing import Callable, Optional

from .exceptions import HTTPException
from .request import Request
from .response import Response
from .routing import Router, scan_class_for_routes


class MaBabarDuaApi:
    def __init__(self, middlewares: Optional[list[Callable]] = None) -> None:
        self.router = Router()
        self._global_middlewares: list[Callable] = middlewares or []

    async def __call__(self, scope: dict, receive: Callable, send: Callable) -> None:
        scope_type = scope["type"]
        if scope_type == "lifespan":
            await self._handle_lifespan(receive, send)
        elif scope_type == "http":
            await self._handle_http(scope, receive, send)

    async def _handle_http(
        self, scope: dict, receive: Callable, send: Callable
    ) -> None:
        request = Request(scope, receive)
        try:
            response = await self.router.resolve(request, self._global_middlewares)
        except HTTPException as exc:
            response = Response(content=exc.detail, status_code=exc.status_code)
        except Exception:
            response = Response(content="Internal Server Error", status_code=500)
        await response._asgi_send(send)

    async def _handle_lifespan(self, receive: Callable, send: Callable) -> None:
        while True:
            event = await receive()
            if event["type"] == "lifespan.startup":
                await send({"type": "lifespan.startup.complete"})
            elif event["type"] == "lifespan.shutdown":
                await send({"type": "lifespan.shutdown.complete"})
                return

    def _register(
        self,
        path: Optional[str],
        method: str,
        handler: Callable,
        middlewares: list[Callable],
    ) -> Callable:
        resolved_path = path or f"/{handler.__name__}"
        self.router.add_route(resolved_path, method, handler, middlewares)
        return handler

    def get(
        self, path: Optional[str] = None, middlewares: Optional[list[Callable]] = None
    ):
        def wrapper(handler: Callable) -> Callable:
            return self._register(path, "GET", handler, middlewares or [])

        return wrapper

    def post(
        self, path: Optional[str] = None, middlewares: Optional[list[Callable]] = None
    ):
        def wrapper(handler: Callable) -> Callable:
            return self._register(path, "POST", handler, middlewares or [])

        return wrapper

    def put(
        self, path: Optional[str] = None, middlewares: Optional[list[Callable]] = None
    ):
        def wrapper(handler: Callable) -> Callable:
            return self._register(path, "PUT", handler, middlewares or [])

        return wrapper

    def route(
        self, path: Optional[str] = None, middlewares: Optional[list[Callable]] = None
    ):
        def wrapper(cls):
            if not isinstance(cls, type):
                raise ValueError("@route can only decorate classes.")
            resolved_path = path or f"/{cls.__name__}"
            for r in scan_class_for_routes(cls, resolved_path, middlewares or []):
                self.router.routes.append(r)
            return cls

        return wrapper
