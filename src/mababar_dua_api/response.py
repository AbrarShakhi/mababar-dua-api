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

    def send(self, content: Any = "", status_code: int = 200) -> None:
        self._content = content if isinstance(content, str) else str(content)
        self._status_code = int(status_code)

    def json(self, data: Any, status_code: int = 200) -> None:
        self._content = json.dumps(data)
        self._status_code = status_code
        self._extra_headers["content-type"] = "application/json"

    def render(self, template_name: str, context: dict = {}) -> None:
        path = f"{template_name}.html"
        with open(path) as fp:
            template = fp.read()
        for key, value in context.items():
            template = re.sub(
                r"{{\s*" + re.escape(key) + r"\s*}}", str(value), template
            )
        self._content = template
        self._status_code = 200
        self._extra_headers["content-type"] = "text/html; charset=utf-8"

    def _build_headers(self) -> list[tuple[bytes, bytes]]:
        headers: dict[str, str] = {"content-type": f"{self.media_type}; charset=utf-8"}
        headers.update(self._extra_headers)
        return [
            (k.lower().encode("latin-1"), v.encode("latin-1"))
            for k, v in headers.items()
        ]


class JSONResponse(Response):
    media_type = "application/json"

    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: Optional[dict] = None,
    ) -> None:
        super().__init__(
            content=json.dumps(content),
            status_code=status_code,
            headers=headers,
        )

    def _build_headers(self) -> list[tuple[bytes, bytes]]:
        headers: dict[str, str] = {"content-type": "application/json"}
        headers.update(self._extra_headers)
        return [
            (k.lower().encode("latin-1"), v.encode("latin-1"))
            for k, v in headers.items()
        ]


class HTMLResponse(Response):
    media_type = "text/html"

    def __init__(
        self,
        content: Any = None,
        status_code: int = 200,
        headers: Optional[dict] = None,
    ) -> None:
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
        )

    def _build_headers(self) -> list[tuple[bytes, bytes]]:
        headers: dict[str, str] = {"content-type": "text/html; charset=utf-8"}
        headers.update(self._extra_headers)
        return [
            (k.lower().encode("latin-1"), v.encode("latin-1"))
            for k, v in headers.items()
        ]
