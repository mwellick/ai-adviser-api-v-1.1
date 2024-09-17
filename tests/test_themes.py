import pytest
from database.models import Theme
from .conftest import TestSessionLocal
from httpx import AsyncClient
from starlette import status


@pytest.fixture
async def create_theme(ac: AsyncClient):
    theme = Theme(
        name="Test Theme",
        description="test description"
    )
    db = TestSessionLocal()
    db.add(theme)
    await db.commit()


async def test_themes_list(create_theme, ac: AsyncClient):
    response = await ac.get("/themes/")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        "id": 1,
        "name": "Test Theme",
        "description": "test description"
    }]
    assert len(response.json()) == 1
