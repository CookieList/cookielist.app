import io
import pathlib

import brotli
import numpy
from numpy.typing import NDArray
from rich import progress

from cookielist.environment import env


class DataBaseFile:
    def __init__(self, database: pathlib.Path) -> None:
        self.database_file = database.resolve()
        self.__chunk_size = 1024 * 32
        self.__brotli_level = 11

    def read_database(self) -> NDArray:
        _np = io.BytesIO()
        _np.write(brotli.decompress(self.database_file.read_bytes()))
        _np.seek(0)
        return numpy.load(_np, allow_pickle=True)

    def write_database(self, **contents: list[list[str | int | list[str]]]) -> None:
        _np = io.BytesIO()
        _br = brotli.Compressor(quality=self.__brotli_level, mode=brotli.MODE_GENERIC)
        numpy.savez(_np, **contents)
        _size = _np.tell()
        _np.seek(0)
        progress_bar = progress.Progress(
            progress.TextColumn("[red]SAVING[/red]"),
            progress.TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            progress.BarColumn(),
            progress.TimeElapsedColumn(),
            progress.TextColumn("•"),
            progress.TimeRemainingColumn(),
            refresh_per_second=1 / 8 if env.bool("GITHUB_ACTIONS", False) else 10,
        )

        with progress_bar as pbar:
            steps = (_size // self.__chunk_size) + (
                1 if _size % self.__chunk_size != 0 else 0
            )
            with self.database_file.open("wb") as _dbf:
                for _ in pbar.track(range(steps)):
                    chunk = _np.read(self.__chunk_size)
                    _dbf.write(_br.process(chunk))
                    _dbf.write(_br.flush())
                _dbf.write(_br.finish())

    def swap_db(self, database: pathlib.Path) -> None:
        if database.exists() and database.is_file():
            try:
                self.database_file.unlink(missing_ok=True)
                self.database_file.write_bytes(database.read_bytes())
                return True
            except Exception:
                pass
        return False
