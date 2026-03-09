from typing import Optional, List, Dict, Any
from aussiebb import AussieBB
import json
import os
import subprocess
import sys

import pytest
from aussiebb.types import AussieBBConfigFile

from aussiebb_outage_watcher import configloader
from aussiebb_outage_watcher.__main__ import do_the_thing, main


def make_outage_payload() -> dict[str, list[dict[str, object]]]:
    return {
        "networkEvents": [
            {
                "reference": 12345,
                "title": "Network Maintenance",
                "summary": "Planned work",
                "start_time": "2026-03-09T00:00:00Z",
                "end_time": "2026-03-09T01:00:00Z",
                "restored_at": None,
                "last_updated": None,
            }
        ],
        "aussieOutages": [],
        "currentNbnOutages": [],
        "scheduledNbnOutages": [],
        "resolvedScheduledNbnOutages": [],
        "resolvedNbnOutages": [],
    }


class FakeUser(AussieBB):
    def __init__(
        self,
        *,
        username: str = "test@example.com",
        services: list[dict[str, int]] | None = None,
        outages_by_service: dict[int, dict[str, list[dict[str, object]]] | Exception] | None = None,
        services_error: Exception | None = None,
    ) -> None:
        self.username = username
        self._services = services or [{"service_id": 1}]
        self._outages_by_service = outages_by_service or {1: make_outage_payload()}
        self._services_error = services_error

    def get_services(
        self,
        page: int = 1,
        use_cached: bool = False,
        servicetypes: Optional[List[str]] = None,
        drop_types: Optional[List[str]] = None,
    ) -> Optional[List[Dict[str, Any]]]:
        del use_cached
        if self._services_error is not None:
            raise self._services_error
        return self._services

    def service_outages(self, service_id: int) -> dict[str, list[dict[str, object]]]:
        result = self._outages_by_service[service_id]
        if isinstance(result, Exception):
            raise result
        return result


def test_configloader_returns_empty_config_when_no_files_exist(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    home_dir = tmp_path / "home"
    home_dir.mkdir()

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(home_dir))

    config = configloader()

    assert config.users == []


def test_configloader_reads_local_config(monkeypatch: pytest.MonkeyPatch, tmp_path) -> None:
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    config_path = tmp_path / "aussiebb.json"
    config_path.write_text(
        json.dumps(
            {
                "users": [
                    {
                        "username": "demo@example.com",
                        "password": "hunter2",
                    }
                ]
            }
        )
    )

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(home_dir))

    config = configloader()

    assert config.users[0].username == "demo@example.com"
    assert config.users[0].password.get_secret_value() == "hunter2"


def test_configloader_exits_on_json_decode_error(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    home_dir = tmp_path / "home"
    home_dir.mkdir()
    config_path = tmp_path / "aussiebb.json"
    config_path.write_text("{}")

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("HOME", str(home_dir))
    monkeypatch.setattr(
        "aussiebb_outage_watcher.AussieBBConfigFile.model_validate_json",
        lambda _contents: (_ for _ in ()).throw(
            json.JSONDecodeError("Expecting value", "{}", 0)
        ),
    )

    with pytest.raises(SystemExit) as excinfo:
        configloader()

    assert str(excinfo.value) == "Failed to parse config file: Expecting value: line 1 column 1 (char 0)"


def test_do_the_thing_prints_outage_json(capsys: pytest.CaptureFixture[str]) -> None:
    do_the_thing([FakeUser()])

    captured = capsys.readouterr()
    payload = json.loads(captured.out.strip())

    assert payload["account_username"] == "test@example.com"
    assert payload["networkEvents"][0]["reference"] == 12345
    assert payload["networkEvents"][0]["title"] == "Network Maintenance"
    assert payload["_time"].endswith("+00:00")


def test_do_the_thing_continues_after_service_outage_error(
    capsys: pytest.CaptureFixture[str],
) -> None:
    user = FakeUser(
        services=[{"service_id": 1}, {"service_id": 2}],
        outages_by_service={
            1: RuntimeError("temporary failure"),
            2: make_outage_payload(),
        },
    )

    do_the_thing([user])

    captured = capsys.readouterr().out.strip().splitlines()

    assert captured[0] == "Failed to run get_services(1): temporary failure"
    payload = json.loads(captured[1])
    assert payload["networkEvents"][0]["reference"] == 12345


def test_main_exits_when_no_users_configured(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    monkeypatch.setattr(
        "aussiebb_outage_watcher.__main__.configloader",
        lambda: AussieBBConfigFile.model_validate({"users": []}),
    )

    with pytest.raises(SystemExit) as excinfo:
        main()

    assert excinfo.value.code == 1
    assert capsys.readouterr().out.strip() == "No users found in config, exiting."


def test_cli_exits_cleanly_without_config(tmp_path) -> None:
    home_dir = tmp_path / "home"
    home_dir.mkdir()

    env = os.environ.copy()
    env["HOME"] = str(home_dir)

    result = subprocess.run(
        [sys.executable, "-m", "aussiebb_outage_watcher"],
        cwd=tmp_path,
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert result.stdout.strip() == "No users found in config, exiting."
