import typing
from collections import namedtuple
from dataclasses import dataclass

import numpy
import orjson
from numpy.typing import NDArray
from rich import progress

from cookielist.assets import asset
from cookielist.database.constants import dbconstants
from cookielist.environment import env
from cookielist.utils import AnilistClient

AnilistResponseRelationType = namedtuple("Relation", ["id", "relation"])


@dataclass(repr=False, eq=False, frozen=True)
class AnilistResponseType:
    __slots__ = (
        "id",
        "format",
        "status",
        "type",
        "duration",
        "chapters",
        "episodes",
        "next_airing",
        "relations",
        "start_date",
        "title_english",
        "title_romaji",
        "title_native",
        "cover_image",
    )

    id: int
    format: str
    status: str
    type: str
    duration: int
    chapters: int
    episodes: int
    next_airing: int | None
    relations: list[tuple[str, str]]
    start_date: AnilistResponseRelationType  # TODO: Wrong type hint
    title_english: str
    title_romaji: str
    title_native: str
    cover_image: str


class DataBaseOperations:
    def __init__(self) -> None:
        self.anilist = AnilistClient(asset.path("database.graphql"))

    def create_database(
        self, parser: typing.Callable = lambda _: _
    ) -> list[list[str | int | list[str]]]:
        media = list()
        progress_bar = progress.Progress(
            progress.TextColumn("[red]FETCHING[/red]"),
            progress.TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            progress.BarColumn(),
            progress.MofNCompleteColumn(),
            progress.TextColumn("•"),
            progress.TimeElapsedColumn(),
            progress.TextColumn("•"),
            progress.TimeRemainingColumn(),
            refresh_per_second=1 / 8 if env.bool("GITHUB_ACTIONS", False) else 10,
        )

        last_al_page = env.int("DATABASE_LAST_PAGE_ESTIMATE", None)
        if last_al_page is None:
            last_al_page = self.anilist.estimate_end_page_of_query(
                "LastPageEstimate", "page"
            )

        with progress_bar as pbar:
            for page in pbar.track(range(1, int(last_al_page / 6) + 1)):
                factor = (page - 1) * 6
                artifact = env.path("COOKIELIST_STATE_FOLDER").joinpath(
                    ".prefetch", f"database.fetch.{page}.json"
                )
                if artifact.exists():
                    _response = orjson.loads(artifact.read_bytes())
                else:
                    _response = self.anilist.query(
                        "DatabaseInfo",
                        sort="ID",
                        _page_1st=factor + 1,
                        _page_2nd=factor + 2,
                        _page_3rd=factor + 3,
                        _page_4th=factor + 4,
                        _page_5th=factor + 5,
                        _page_6th=factor + 6,
                    )
                response = (
                    _response["_page_1st"]["media"]
                    + _response["_page_2nd"]["media"]
                    + _response["_page_3rd"]["media"]
                    + _response["_page_4th"]["media"]
                    + _response["_page_5th"]["media"]
                    + _response["_page_6th"]["media"]
                )
                parsed = list(
                    map(
                        parser,
                        map(self.__prase_al_api_response, response),
                    )
                )
                media.extend(parsed)
        return numpy.asarray(media, dtype="object")

    @staticmethod
    def create_database_mapping(database) -> NDArray:
        __id_index = dbconstants.DB_ENTRY_TABLE_INDEX["ID"]
        return numpy.asarray(
            [[item[__id_index], index] for index, item in enumerate(database)]
        )

    @staticmethod
    def __prase_al_api_response(group: dict) -> AnilistResponseType:
        return AnilistResponseType(
            id=int(group["id"]),
            format=group["format"],
            status=group["status"],
            type=group["type"],
            duration=group["duration"],
            chapters=group["chapters"],
            episodes=group["episodes"],
            next_airing=(
                group["nextAiringEpisode"]["episode"]
                if group["nextAiringEpisode"]
                else None
            ),
            relations=list(
                AnilistResponseRelationType(
                    int(edge["node"]["id"]), edge["relationType"]
                )
                for edge in group["relations"]["edges"]
            ),
            start_date=(
                group["startDate"]["year"],
                group["startDate"]["month"],
                group["startDate"]["day"],
            ),
            title_english=group["title"]["english"]
            or group["title"]["romaji"]
            or group["title"]["native"],
            title_romaji=group["title"]["romaji"]
            or group["title"]["english"]
            or group["title"]["native"],
            title_native=group["title"]["native"]
            or group["title"]["romaji"]
            or group["title"]["english"],
            cover_image=group["coverImage"]["large"],
        )
