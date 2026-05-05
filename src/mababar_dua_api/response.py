import json
import re
from typing import Any, Callable, Optional


class Response:
    media_type = "text/plain"

    def __init__(
        self,
        content: str = "",
        status_code: int = 200,
        headers: Optional[dict] = None,
    ) -> None:
        self._content = content
        self._status_code = status_code
        self._extra_headers: dict[str, str] = headers or {}
