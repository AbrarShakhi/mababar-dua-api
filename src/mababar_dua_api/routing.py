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

def scan_class_for_routes(
    cls: type,
    path: str,
    middlewares: list[Callable],
) -> list[Route]:
    return None