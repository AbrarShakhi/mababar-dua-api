import inspect
from dataclasses import dataclass, field
from typing import Callable, Optional

from parse import parse

from .exceptions import HTTPException
from .middleware import run_middlewares
from .request import Request
from .response import Response

SUPPORTED_METHODS = {"GET", "POST", "PUT", "PATCH", "DELETE"}


@dataclass
class Route:
    path: str
    method: str
    handler: Callable
    middlewares: list[Callable] = field(default_factory=list)


class Router:
    def __init__(self) -> None:
        self.routes: list[Route] = []

    def add_route(
        self,
        path: str,
        method: str,
        handler: Callable,
        middlewares: list[Callable],
    ) -> None:
        self.routes.append(
            Route(
                path=path,
                method=method.upper(),
                handler=handler,
                middlewares=middlewares,
            )
        )

    async def resolve(
        self, request: Request, global_middlewares: list[Callable]
    ) -> Response:
        await run_middlewares(global_middlewares, request)

        for route in self.routes:
            parsed = parse(route.path, request.path)
            if parsed is not None and route.method == request.method:
                request.path_params = parsed.named
                await run_middlewares(route.middlewares, request)

                response = Response(status_code=404)
                if inspect.iscoroutinefunction(route.handler):
                    ret = await route.handler(request, response, **parsed.named)
                else:
                    ret = route.handler(request, response, **parsed.named)
                return ret if isinstance(ret, Response) else response

        raise HTTPException(404, f"No route found for {request.method} {request.path}")


def scan_class_for_routes(
    cls: type,
    path: str,
    middlewares: list[Callable],
) -> list[Route]:
    routes: list[Route] = []
    members = inspect.getmembers(
        cls,
        predicate=lambda x: (inspect.isfunction(x) or inspect.ismethod(x))
        and not (x.__name__.startswith("__") and x.__name__.endswith("__"))
        and x.__name__.upper() in SUPPORTED_METHODS,
    )
    for fn_name, fn_handler in members:
        routes.append(
            Route(
                path=path,
                method=fn_name.upper(),
                handler=fn_handler,
                middlewares=middlewares,
            )
        )
    return routes
