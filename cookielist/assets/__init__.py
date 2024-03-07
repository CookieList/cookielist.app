from functools import cache
from pathlib import Path
from typing import Literal

__all__ = ["asset"]


class __Assets:

    def __init__(self) -> None:
        self.rootPath = Path(__file__).parent

    @cache
    def _path__(self, *directories: str) -> Path | None:
        path = self.rootPath.joinpath(*directories)
        if path.exists() and path.is_file():
            return path

    @cache
    def _content__(
        self, *directories: str, mode: Literal["string", "binary"] = "string"
    ) -> str | bytes | None:
        path = self.path(*directories)
        if path is not None:
            if mode == "binary":
                return path.read_bytes()
            elif mode == "string":
                return path.read_text(encoding="utf-8")

    def path(self, *directories: str) -> Path | None:
        return self._path__(*directories)

    def content(
        self, *directories: str, mode: Literal["string", "binary"] = "string"
    ) -> str | bytes | None:
        return self._content__(*directories, mode=mode)


asset = __Assets()
