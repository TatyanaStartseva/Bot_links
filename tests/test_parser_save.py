import os
import sys
import pytest
from unittest.mock import AsyncMock

# Добавляем путь к директории с parser_save
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Parser')))

from parser_save import insert_many, retry, Chats, Users

import pytest
from unittest.mock import AsyncMock, MagicMock
from parser_save import Users

import pytest
import datetime
from unittest.mock import AsyncMock, MagicMock
from parser_save import Users, Chats


@pytest.mark.asyncio
async def test_users_inserts_valid_users_and_links():
    # Создание данных
    data = {
        "accounts": {
            123: {
                "info": {
                    "username": "testuser",
                    "first_name": "Test",
                    "last_name": "User",
                    "last_online": "2024-05-01 12:00:00",
                    "bio": "Some bio",
                    "premium": True,
                    "phone": "1234567890",
                    "image": True,
                },
                "chats": {111, 222}
            }
        },
        "chats": {111: {}, 222: {}}
    }

    # Моки
    mock_users = AsyncMock()
    mock_users.distinct.return_value = []

    mock_links = MagicMock()
    mock_links.find.return_value = iter([])  # возвращает итерируемый объект, не корутину
    mock_links.insert_many = AsyncMock()

    mock_db = {
        "users": mock_users,
        "links": mock_links
    }

    await Users(data, mock_db)

    # Проверки
    mock_users.insert_many.assert_called_once()
    inserted_users = mock_users.insert_many.call_args[0][0]
    assert inserted_users[0]["username"] == "testuser"

    mock_links.insert_many.assert_called_once()
    inserted_links = mock_links.insert_many.call_args[0][0]
    assert len(inserted_links) == 2


@pytest.mark.asyncio
async def test_users_skips_invalid_users():
    data = {
        "accounts": {
            1: {
                "info": {
                    "username": None,
                    "first_name": None,
                    "last_name": "User",
                    "last_online": None,
                    "bio": None,
                    "premium": False,
                    "phone": "0000000000",
                    "image": False,
                },
                "chats": {100}
            }
        },
        "chats": {100: {}}
    }

    mock_users = AsyncMock()
    mock_users.distinct.return_value = []

    mock_links = MagicMock()
    mock_links.find.return_value = iter([])
    mock_links.insert_many = AsyncMock()

    mock_db = {
        "users": mock_users,
        "links": mock_links
    }

    await Users(data, mock_db)

    mock_users.insert_many.assert_not_called()
    mock_links.insert_many.assert_called_once()


@pytest.mark.asyncio
async def test_chats_inserts_new_chats():
    data = {
        "chats": {
            1: {
                "parent_link": "https://t.me/test1",
                "children_link": "https://t.me/test1_child",
                "title": "Test Chat",
                "last_online": "2024-01-01 10:00:00",
            },
            2: {
                "parent_link": "https://t.me/test2",
                "children_link": "https://t.me/test2_child",
                "title": "Test Chat 2",
                "last_online": None,
            }
        },
        "accounts": {}
    }

    mock_chats = AsyncMock()
    mock_chats.distinct.return_value = [3]  # 3 не используется, 1 и 2 должны добавиться

    mock_db = {
        "chats": mock_chats
    }

    await Chats(data, mock_db)

    mock_chats.insert_many.assert_called_once()
    inserted = mock_chats.insert_many.call_args[0][0]
    assert len(inserted) == 2
    assert inserted[0]["chat_id"] == 1

