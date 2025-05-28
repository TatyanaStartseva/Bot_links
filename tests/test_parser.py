
import sys
import os

# Добавляем путь к верхнему уровню проекта
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Parser")))

from parser_save import Users, Chats

import pytest
from unittest.mock import AsyncMock



@pytest.mark.asyncio
async def test_users_inserts_only_new_users():
    # Подготовка данных
    data = {
        "accounts": {
            1: {
                "info": {
                    "username": "testuser",
                    "first_name": "Test",
                    "last_name": "User",
                    "last_online": "2023-01-01 00:00:00",
                    "bio": "Test bio",
                    "premium": True,
                    "phone": "1234567890",
                    "image": True,
                },
                "chats": {100}
            }
        },
        "chats": [100]
    }

    mock_db = {
        "users": AsyncMock(),
        "links": AsyncMock(),
    }
    mock_db["users"].distinct.return_value = []
    mock_db["links"].find.return_value = []

    await Users(data, mock_db)

    # Проверяем, что были вызваны insert_many с данными
    assert mock_db["users"].insert_many.call_count == 1
    assert mock_db["links"].insert_many.call_count == 1


@pytest.mark.asyncio
async def test_chats_skips_existing():
    data = {
        "chats": {
            100: {
                "parent_link": "https://t.me/test",
                "children_link": "https://t.me/testchannel",
                "title": "Test Chat",
                "last_online": "2023-01-01 00:00:00"
            }
        }
    }

    mock_db = {
        "chats": AsyncMock(),
    }
    mock_db["chats"].distinct.return_value = [100]

    await Chats(data, mock_db)

    assert mock_db["chats"].insert_many.call_count == 0
