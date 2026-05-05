import pytest
from httpx import ASGITransport, AsyncClient

from mababar_dua_api import MaBabarDuaApi


@pytest.fixture
def app() -> MaBabarDuaApi:
    return MaBabarDuaApi()


@pytest.fixture
async def client(app: MaBabarDuaApi):
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


def make_client(app: MaBabarDuaApi):
    return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")
