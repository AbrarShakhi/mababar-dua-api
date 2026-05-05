import inspect
import types
from typing import Callable

from .request import Request


async def run_middlewares(middlewares: list[Callable], request: Request) -> None:
    for mw in middlewares:
        if not isinstance(mw, (types.FunctionType, types.MethodType)) and not callable(
            mw
        ):
            raise ValueError("Middlewares must be callable.")
        if inspect.iscoroutinefunction(mw):
            await mw(request)
        else:
            mw(request)
