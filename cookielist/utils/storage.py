from cookielist.environment import env
import time

import orjson

_storage_path = (
    env.path("COOKIELIST_STATE_FOLDER").resolve().joinpath("storage.json")
)
if not _storage_path.exists():
    _storage_path.write_bytes(b"{}")
_sync_gap = 24 * 60 * 60


class Storage(dict):
    __last_sync = 0

    def __synchronize(self):
        if (time.time() - self.__last_sync) > _sync_gap:
            _storage_path.write_bytes(orjson.dumps(self))
            self.__last_sync = time.time()

    def sync(self):
        self.__synchronize()

    def __getitem__(self, key):
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        super().__setitem__(str(key), value)
        self.__synchronize()


storage = Storage(orjson.loads(_storage_path.read_bytes()))
