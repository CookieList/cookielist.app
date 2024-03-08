import base64
from time import time as timestamp

import brotli
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import LargeBinary, MetaData, String
from sqlalchemy.orm import DeclarativeBase, Mapped, MappedAsDataclass, mapped_column

from cookielist.assets import asset
from cookielist.environment import env


def get_avatar_id(url: str) -> str:
    return url.split("/")[-1].split(".")[0].split("-")[-1]


def avatar_url_to_binary(url: str) -> bytes:
    response = requests.get(url)
    if response.status_code == 200:
        return brotli.compress(
            base64.encodebytes(response.content).decode().replace("\n", "").encode(),
            quality=8,
        )
    else:
        return brotli.compress(b"")


class Base(DeclarativeBase, MappedAsDataclass):
    metadata = MetaData(
        naming_convention={
            "ix": "ix_%(column_0_label)s",
            "uq": "uq_%(table_name)s_%(column_0_name)s",
            "ck": "ck_%(table_name)s_%(constraint_name)s",
            "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
            "pk": "pk_%(table_name)s",
        }
    )


db = SQLAlchemy(model_class=Base)
images_path = env.path("COOKIELIST_STATE_FOLDER").joinpath("avatars")
DEFAULT_AVATAR = asset.content("avatar.base64.txt")


class CookielistBadge(db.Model):
    __tablename__ = "cookielist_badges_data"
    _static_columns_ = {
        "anilist_user_id",
        "anilist_username",
        "anilist_avatar_url",
        "anilist_profile_theme_color",
        "watched_anime_title_count",
        "watched_manga_title_count",
        "watched_music_title_count",
        "watched_novel_title_count",
        "watched_anime_duration_in_minutes",
        "watched_anime_episodes_count",
        "watched_manga_chapters_count",
        "watched_anime_series_count",
        "watched_music_series_count",
        "watched_manga_series_count",
        "watched_novel_series_count",
    }
    _dynamic_columns_ = {
        "anilist_avatar_image",
        "created_at",
        "updated_at",
    }

    anilist_user_id: Mapped[int] = mapped_column(primary_key=True, unique=True)
    anilist_username: Mapped[str] = mapped_column(String(20), unique=True)
    anilist_avatar_url: Mapped[str]
    anilist_avatar_image = mapped_column(LargeBinary(), default=b"")
    anilist_profile_theme_color: Mapped[str]

    watched_anime_title_count: Mapped[int]
    watched_manga_title_count: Mapped[int]
    watched_music_title_count: Mapped[int]
    watched_novel_title_count: Mapped[int]

    watched_anime_duration_in_minutes: Mapped[int]

    watched_anime_episodes_count: Mapped[int]
    watched_manga_chapters_count: Mapped[int]

    watched_anime_series_count: Mapped[int]
    watched_music_series_count: Mapped[int]
    watched_manga_series_count: Mapped[int]
    watched_novel_series_count: Mapped[int]

    created_at: Mapped[float] = mapped_column(nullable=False)
    updated_at: Mapped[float] = mapped_column(nullable=False)

    def to_dict(self, negatives: list[str] = None) -> dict:
        negatives = negatives or []
        return {
            key: getattr(self, key)
            for key in self._static_columns_
            if key not in negatives
        } | {
            key: getattr(self, key)
            for key in self._dynamic_columns_
            if key not in negatives
        }

    def anilist_avatar_base_64(self):
        if get_avatar_id(self.anilist_avatar_url) == "default":
            return DEFAULT_AVATAR
        image_base_64 = brotli.decompress(self.anilist_avatar_image).decode()
        if image_base_64 == "":
            return DEFAULT_AVATAR
        return (
            f"data:image/"
            + self.anilist_avatar_url.split(".")[-1]
            + ";base64,"
            + image_base_64
        )

    def __repr__(self):
        return f"<User @{self.anilist_username} [{self.anilist_user_id}]>"

    def update_badge(self, data: dict):
        _previous_avatar = self.anilist_avatar_url
        for key, value in data.items():
            if key in self._static_columns_:
                setattr(self, key, value)
        self.updated_at = timestamp()
        if _previous_avatar != self.anilist_avatar_url:
            if get_avatar_id(self.anilist_avatar_url) != "default":
                self.anilist_avatar_image = avatar_url_to_binary(
                    self.anilist_avatar_url
                )
            else:
                self.anilist_avatar_image = b""

    @classmethod
    def create_badge(cls, data: dict):
        new = cls(
            **{
                key: value for key, value in data.items() if key in cls._static_columns_
            },
            created_at=timestamp(),
            updated_at=timestamp(),
        )
        new.ensure_avatar_exists()
        return new

    def ensure_avatar_exists(self):
        if get_avatar_id(self.anilist_avatar_url) != "default":
            self.anilist_avatar_image = avatar_url_to_binary(self.anilist_avatar_url)
        else:
            self.anilist_avatar_image = b""
