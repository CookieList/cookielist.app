import os
from pathlib import Path
from functools import cache
from typing import Any, Callable

import dotenv_vault


class Env:
    def __init__(self) -> None:
        dotenv_id = os.environ.get("DOTENV", "").strip().upper()
        dotenv_key_path = Path(".dotenv.key")
        env_path = Path(".env")

        if dotenv_id:
            key = os.environ.get(f"DOTENV_KEY_{dotenv_id}", "").strip()
            os.environ[
                "DOTENV_KEY"
            ] = f"dotenv://:key_{key}@dotenv.org/vault/.env.vault?environment={dotenv_id.lower()}"
        elif dotenv_key_path.is_file() and dotenv_key_path.exists():
            os.environ["DOTENV_KEY"] = dotenv_key_path.read_text().strip()

        if env_path.exists() and env_path.is_file():
            dotenv_vault.load_dotenv(stream=Path(".env").open("r", encoding="utf-8"))
        else:
            dotenv_vault.load_dotenv()

    @property
    def environ(self):
        return os.environ
    
    def __getitem__(self, __name: str) -> str:
        return os.environ[__name]

    def __call__(self, __name: str, __default: Any = None) -> Any | str:
        return os.environ.get(__name, __default)

    def __contains__(self, __name: str) -> bool:
        return __name in os.environ

    @staticmethod
    def get(
        __name: str, __default: Any = None, __format: Callable = lambda _: _
    ) -> Any:
        env = os.environ.get(__name)
        if env is not None:
            return __format(env)
        else:
            return __default

    def string(self, __name: str, __default: Any = None) -> str:
        return self.get(__name, __default, str)

    def bool(self, __name: str, __default: Any = None) -> bool:
        return str(self.get(__name, __default, str)).lower().strip() in ("true", "1")

    def int(self, __name: str, __default: Any = None) -> int:
        return self.get(__name, __default, int)

    def float(self, __name: str, __default: Any = None) -> float:
        return self.get(__name, __default, float)

    def path(self, __name: str, __default: Any = None) -> Path:
        return self.get(__name, __default, Path)

    def list(self, __name: str, __default: Any = None, __sep: str = ",") -> list:
        return [i.strip() for i in str(self.get(__name, __default, str).strip()).split(__sep) if i.strip()]


env = Env()
