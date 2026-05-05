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

        if scope_type == "http":
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
