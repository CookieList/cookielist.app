import itertools
from collections import namedtuple
from functools import cache, lru_cache
from pathlib import Path
from time import time
from typing import Tuple

import numpy

from cookielist.database.constants import dbconstants
from cookielist.database.io import DataBaseFile
from cookielist.database.operations import DataBaseOperations
from cookielist.database.parser import DataBaseParser
from cookielist.environment import env

ClDbItem = namedtuple("ClDbItem", dbconstants.DB_ENTRY_TABLE)


@cache
class CookieListDatabase(DataBaseFile, DataBaseParser, DataBaseOperations):
    def __init__(
        self,
        database: Path = env.path("COOKIELIST_STATE_FOLDER").joinpath("cookielist.db"),
    ) -> None:
        DataBaseFile.__init__(self, database)
        DataBaseParser.__init__(self)
        DataBaseOperations.__init__(self)

        self.synchronize()

    def __contains__(self, id: int) -> bool:
        return id in self.__map

    @lru_cache(maxsize=64)
    def __getitem__(self, _get: int | Tuple[int, str]):
        if isinstance(_get, int):
            return ClDbItem(*self.__db[self.__map[_get]])
        else:
            return self.__db[self.__map[_get[0]]][
                dbconstants.DB_ENTRY_TABLE_INDEX[_get[1]]
            ]

    def __call__(self, id: int):
        return self.__relation_table[id]

    @property
    def is_db_created_now(self):
        try:
            return self.__db_creation_time
        except Exception:
            return None

    def synchronize(self, max_retries: int = 2, force_recreate: bool = False) -> None:
        retries = 0
        if (not self.database_file.exists()) or force_recreate:
            while True:
                try:
                    db = self.create_database(parser=self.parse_al_media)
                    break
                except Exception:
                    retries += 1
                    if retries > max_retries:
                        raise Exception
            self.__db_creation_time = time()
            self.write_database(database=db, mapping=self.create_database_mapping(db))
        else:
            self.__db_creation_time = None

        __db = self.read_database()
        self.__db = __db["database"]
        self.__map = dict(__db["mapping"])

        __relations_position = dbconstants.DB_ENTRY_TABLE_INDEX["RELATIONS"]
        relations = self.parse_relation(
            list(
                itertools.chain.from_iterable(
                    [item[__relations_position]] for item in self.__db
                )
            ),
            self,
        )

        self.__relation_table = numpy.asarray(
            [value[0] for value in relations], dtype="object"
        )

        self.__relation_index = {
            value: index
            for index, _value in enumerate(relations)
            for value in _value[0]
        }

        self.__series_index = {
            media: series for group, series in relations for media in group
        }

    def relation(self, id: int):
        return self.__relation_index[id]

    def series(self, id: int):
        return self.__series_index[id]
