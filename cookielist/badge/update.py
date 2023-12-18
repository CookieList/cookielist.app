import base64
from functools import cache
from pathlib import Path

import requests_cache
from flask import url_for

from cookielist.utils import BadgeCacheHandler
from cookielist.environment import env


@cache
class BadgeManager:
    def __init__(self) -> None:
        self.http_session = requests_cache.CachedSession(
            cache_name=str(
                env.path("COOKIELIST_STATE_FOLDER").joinpath("images.sqlite")
            )
        )
        self.badge_cdn = BadgeCacheHandler()

    def __img_to_b64(self, uri: str, id: int = None) -> str:
        img_response = self.http_session.get(uri)
        img_byte = img_response.content
        img_type = uri.split(".")[-1]

        if img_response.status_code != 200:
            previous_record = self.badge_cdn.get(id, None)

            if previous_record is not None:
                return previous_record["avatarB64"]
            else:
                img_type = "png"
                img_byte = b""  # TODO: default image

        return "data:image/{img_type};base64,".format(
            img_type=img_type
        ) + base64.encodebytes(img_byte).decode().replace("\n", "")

    def __calculate_badge_data(self, user: dict, result: dict) -> dict:
        return dict(
            id=user["id"],
            name=user["name"],
            avatarURL=user["avatar"]["large"],
            siteUrl=user["siteUrl"],
            profileColor=user["options"]["profileColor"],
            animeCount=sum(map(lambda _: _["completed"], result["ANIME"]["entries"])),
            mangaCount=sum(map(lambda _: _["completed"], result["MANGA"]["entries"])),
            musicCount=sum(map(lambda _: _["completed"], result["MUSIC"]["entries"])),
            novelCount=sum(map(lambda _: _["completed"], result["NOVEL"]["entries"])),
            animeMinutes=user["statistics"]["anime"]["minutesWatched"],
            animeEpisodes=user["statistics"]["anime"]["episodesWatched"],
            mangaChapters=user["statistics"]["manga"]["chaptersRead"],
            animeSeries=result["ANIME"]["length"],
            musicSeries=result["MUSIC"]["length"],
            mangaSeries=result["MANGA"]["length"],
            novelSeries=result["NOVEL"]["length"],
            avatarB64=self.__img_to_b64(user["avatar"]["large"], id=user["id"]),
        )

    def update_badge_data(self, user: dict, result: dict) -> dict:
        content = self.__calculate_badge_data(user, result)
        self.badge_cdn.update(user["id"], content)

        content["URI"] = url_for("BadgeView:get_badge", id=user["id"])
        del content["avatarB64"]

        return content
