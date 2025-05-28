import os
import  sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Parser')))
from unittest.mock import AsyncMock

import pytest
from parser_save import insert_many, retry, Chats, Users
@pytest.mark.asyncio
async def test_users_skips_users_without_username_or_first_name():
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
        "chats": [100]
    }

    mock_db = {
        "users": AsyncMock(),
        "links": AsyncMock(),
    }
    mock_db["users"].distinct.return_value = []
    mock_db["links"].find.return_value = []

    await Users(data, mock_db)

    # Никакие данные не должны быть вставлены
    assert mock_db["users"].insert_many.call_count == 0
    assert mock_db["links"].insert_many.call_count == 1  # ссылки всё равно должны добавиться


@pytest.mark.asyncio
async def test_chats_inserts_new_chats():
    data = {
        "chats": {
            101: {
                "parent_link": "https://t.me/parent",
                "children_link": "https://t.me/child",
                "title": "Test Channel",
                "last_online": "2023-05-01 10:00:00"
            }
        }
    }

    mock_db = {
        "chats": AsyncMock()
    }
    mock_db["chats"].distinct.return_value = []  # Чат новый

    await Chats(data, mock_db)

    # insert_many должен быть вызван 1 раз
    assert mock_db["chats"].insert_many.call_count == 1
    args, _ = mock_db["chats"].insert_many.call_args
    assert args[0][0]["chat_id"] == 101

@pytest.mark.asyncio
async def test_insert_many_empty_list_does_not_call_db():
    mock_conn = {
        "table": AsyncMock()
    }

    await insert_many(mock_conn, "table", [])

    # insert_many не должен быть вызван
    mock_conn["table"].insert_many.assert_not_called()


@pytest.mark.asyncio
async def test_retry_retries_on_exception(monkeypatch):
    call_counter = {"count": 0}

    async def failing_func():
        call_counter["count"] += 1
        if call_counter["count"] < 3:
            raise Exception("fail")
        return

    await retry(failing_func)

    assert call_counter["count"] == 3  # Убедимся, что были попытки повторов
