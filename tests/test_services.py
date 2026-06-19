import json
from pathlib import Path
from unittest.mock import AsyncMock

import pytest

from services import load_users, save_users


def make_users_file(path: Path, data: dict[str, str]) -> None:
    """Записать тестовый JSON в файл."""
    path.write_text(json.dumps(data), encoding="utf-8")


class TestLoadUsers:
    def test_returns_empty_dict_when_file_missing(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        fake = tmp_path / "nonexistent.json"
        monkeypatch.setattr("services.USERS_FILE", fake)
        assert load_users() == {}

    def test_reads_existing_file(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        fake = tmp_path / "users.json"
        make_users_file(fake, {"123": "alice", "456": "bob"})
        monkeypatch.setattr("services.USERS_FILE", fake)
        assert load_users() == {"123": "alice", "456": "bob"}


class TestSaveUsers:
    def test_writes_and_reads_back(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        fake = tmp_path / "users.json"
        monkeypatch.setattr("services.USERS_FILE", fake)

        save_users({"789": "charlie"})

        assert load_users() == {"789": "charlie"}

    def test_overwrites_existing_data(
        self,
        monkeypatch: pytest.MonkeyPatch,
        tmp_path: Path,
    ) -> None:
        fake = tmp_path / "users.json"
        make_users_file(fake, {"111": "old"})
        monkeypatch.setattr("services.USERS_FILE", fake)

        save_users({"222": "new"})

        assert load_users() == {"222": "new"}
