import json
from typing import Any, Callable, Optional
from urllib.parse import parse_qs


class Request:
    def __init__(self, scope: dict, receive: Callable) -> None:
        self._scope = scope
        self._receive = receive
        self._body: Optional[bytes] = None

        self.method: str = scope["method"].upper()
        self.path: str = scope["path"]
        self.path_params: dict = {}

        raw_qs = scope.get("query_string", b"")
        self.queries: dict = self._parse_query_string(raw_qs)

        raw_headers: list[tuple[bytes, bytes]] = scope.get("headers", [])
        self.headers: dict[str, str] = {
            k.decode("latin-1").lower(): v.decode("latin-1")
            for k, v in raw_headers
        }

    @staticmethod
    def _parse_query_string(raw: bytes) -> dict:
        if not raw:
            return {}
        parsed = parse_qs(raw.decode("latin-1"), keep_blank_values=True)
        return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}

    async def body(self) -> bytes:
        if self._body is None:
            chunks: list[bytes] = []
            while True:
                event = await self._receive()
                chunks.append(event.get("body", b""))
                if not event.get("more_body", False):
                    break
            self._body = b"".join(chunks)
        return self._body

    async def json(self) -> Any:
        raw = await self.body()
        return json.loads(raw)

    async def text(self) -> str:
        raw = await self.body()
        return raw.decode("utf-8")
