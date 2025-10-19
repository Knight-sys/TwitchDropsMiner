from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypedDict

from yarl import URL

from src.config import DEFAULT_LANG, SETTINGS_PATH
from src.utils import json_load, json_save


if TYPE_CHECKING:
    from typing import Any as ParsedArgs  # Avoid circular import


class SettingsFile(TypedDict):
    proxy: URL
    language: str
    dark_mode: bool
    games_to_watch: list[str]
    connection_quality: int
    minimum_refresh_interval_minutes: int


default_settings: SettingsFile = {
    "proxy": URL(),
    "games_to_watch": [],
    "dark_mode": False,
    "connection_quality": 1,
    "language": DEFAULT_LANG,
    "minimum_refresh_interval_minutes": 30,
}


class Settings:
    # from args
    log: bool
    dump: bool
    # args properties
    debug_ws: int
    debug_gql: int
    logging_level: int
    # from settings file
    proxy: URL
    language: str
    dark_mode: bool
    games_to_watch: list[str]
    connection_quality: int
    minimum_refresh_interval_minutes: int

    PASSTHROUGH = ("_settings", "_args", "_altered")

    def __init__(self, args: ParsedArgs):
        self._settings: SettingsFile = json_load(SETTINGS_PATH, default_settings)
        self._args: ParsedArgs = args
        self._altered: bool = False

    # default logic of reading settings is to check args first, then the settings file
    def __getattr__(self, name: str, /) -> Any:
        if name in self.PASSTHROUGH:
            # passthrough
            return getattr(super(), name)
        elif hasattr(self._args, name):
            return getattr(self._args, name)
        elif name in self._settings:
            return self._settings[name]  # type: ignore[literal-required]
        return getattr(super(), name)

    def __setattr__(self, name: str, value: Any, /) -> None:
        if name in self.PASSTHROUGH:
            # passthrough
            return super().__setattr__(name, value)
        elif name in self._settings:
            self._settings[name] = value  # type: ignore[literal-required]
            self._altered = True
            return
        raise TypeError(f"{name} is missing a custom setter")

    def __delattr__(self, name: str, /) -> None:
        raise RuntimeError("settings can't be deleted")

    def alter(self) -> None:
        self._altered = True

    def save(self, *, force: bool = False) -> None:
        if self._altered or force:
            json_save(SETTINGS_PATH, self._settings, sort=True)
