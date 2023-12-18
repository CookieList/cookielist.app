from cookielist.environment import env
import time
from collections import deque
from functools import cache
from pathlib import Path
from typing import Any

import brotli
import orjson


@cache
class BadgeCacheHandler:
    def __init__(self) -> None:
        self.STORAGE = env.path("COOKIELIST_STATE_FOLDER").joinpath(".badgecdn")
        self.STORAGE.mkdir(exist_ok=True, parents=True)

        self.__cache: dict[int, dict[str, str]] = {}
        self.__item_order = deque([])
        self.__cache_size = 0

        self.__item_limit = 128
        self.__disk_interval = int((24 * 60) * 60)

    @property
    def cache_items(self) -> list[int]:
        return list(self.__cache.keys())

    @property
    def cache_count(self) -> int:
        return self.__cache_size

    def get(self, id: int, _default: Any = None):
        cache = self.__cache.get(id, None)
        if cache is None:
            content_file = self.STORAGE.joinpath(str(id))
            if content_file.exists():
                cache = orjson.loads(brotli.decompress(content_file.read_bytes()))
                cache["__from_file_system"] = True
            else:
                return _default
        else:
            cache["__from_file_system"] = False
        return cache

    def update(self, id: int, content: dict):
        content = content.copy()
        content_file = self.STORAGE.joinpath(str(id))

        if id not in self.__item_order:
            self.__cache[id] = content

            self.__cache_size += 1
            self.__item_order.appendleft(id)
            self.__cache[id]["__last_disk_write"] = time.time()
            content_file.write_bytes(
                brotli.compress(
                    orjson.dumps(self.__cache[id]),
                    quality=8,
                )
            )
        else:
            self.__cache[id].update(content)

            if (
                time.time() - self.__cache[id]["__last_disk_write"]
            ) > self.__disk_interval:
                content_file.write_bytes(
                    brotli.compress(
                        orjson.dumps(content),
                        quality=8,
                    )
                )

        if self.__cache_size >= self.__item_limit:
            del self.__cache[self.__item_order.pop()]
