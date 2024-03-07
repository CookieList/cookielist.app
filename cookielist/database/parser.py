import collections
from typing import Generator

import arrow

from cookielist.database.constants import dbconstants
from cookielist.database.operations import AnilistResponseType


class DataBaseParser:
    def __init__(self) -> None:
        pass

    @staticmethod
    def __find_media_type(media_format: str, media_type: str) -> str:
        if (
            media_format == dbconstants.MUSIC_FORMAT
            or media_format == dbconstants.NOVEL_FORMAT
        ):
            return media_format
        return media_type

    @staticmethod
    def __convert_to_timestamp(year: int, month: int, day: int) -> int:
        try:
            return int(
                arrow.Arrow(
                    year=year,
                    month=month or 1,
                    day=day or 1,
                ).timestamp()
            )
        except:
            return int(arrow.now().timestamp())

    @staticmethod
    def __generator_to_list(func) -> list:
        def inner_wrap(*args, **kwargs):
            return list(func(*args, **kwargs))

        return inner_wrap

    @staticmethod
    @__generator_to_list
    def __merge_lists_with_common_elements(data: list[str]) -> Generator[str, None, None]:
        neighbors = collections.defaultdict(set)
        seen = set()
        for each in data:
            for item in each:
                neighbors[item].update(each)

        def component(node, neighbors=neighbors, seen=seen, see=seen.add):
            nodes = set([node])
            next_node = nodes.pop
            while nodes:
                node = next_node()
                see(node)
                nodes |= neighbors[node] - seen
                yield node

        for node in neighbors:
            if node not in seen:
                yield sorted(component(node))

    def parse_al_media(self, media: AnilistResponseType) -> list[str | int | list[str]]:
        media_count = (
            media.chapters
            if media.chapters
            else (
                media.next_airing
                if media.next_airing
                else media.episodes if media.episodes else 0
            )
        )
        media_type = self.__find_media_type(media.format, media.type)
        media_duration = round(
            (
                0
                if media.format in dbconstants.READ_TYPES
                else (media_count * (media.duration or 0)) * 60
            ),
            2,
        )
        media_start = self.__convert_to_timestamp(*media.start_date)
        media_relations = [
            edge.id
            for edge in media.relations
            if edge.relation in dbconstants.ALLOWED_RELATIONS
        ] + [media.id]

        return [
            media.id,  # ID
            media.title_english,  # NAME
            media.title_romaji,  # NAME
            media.title_native,  # NAME
            media.cover_image,  # COVER
            media.format,  # FORMAT
            media.status,  # STATUS
            media_type,  # TYPE
            media_count,  # COUNT
            media_duration,  # DURATION
            media_start,  # START
            media_relations,  # RELATIONS
        ]

    @__generator_to_list
    def parse_relation(self, relations, media):
        relations = self.__merge_lists_with_common_elements(relations)
        priority = collections.defaultdict(
            lambda: float("inf"),
            {
                format: index
                for index, format in enumerate(
                    dbconstants.RELATION_PARSE_PRIORITY_ORDER, start=1
                )
            },
        )

        def _first_of_series(group):
            return sorted(
                group, key=lambda media_id: priority[media[media_id, "FORMAT"]]
            )[0]

        def _spilt_relation_types(relation_group):
            for media_type in dbconstants.MEDIA_TYPES:
                yield list(
                    filter(
                        lambda media_id: media[media_id, "TYPE"] == media_type,
                        relation_group,
                    )
                )

        for relation in relations:
            if len(relation) == 1:
                yield relation, relation[0]
            else:
                for group in _spilt_relation_types(
                    sorted(relation, key=lambda media_id: media[media_id, "START"])
                ):
                    if group:
                        yield group, _first_of_series(group)
