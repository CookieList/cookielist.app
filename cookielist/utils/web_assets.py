import pathlib
import shutil
import time
from typing import Generator

import orjson
from flask import Flask
from wcmatch import glob, wcmatch

from cookielist.environment import env

try:
    from cookielist.utils.assetfilters import WebAssetFilters
except ImportError:
    WebAssetFilters = lambda: None

GLOB_FLAGS = wcmatch.RECURSIVE | glob.GLOBSTAR | wcmatch.PATHNAME | glob.EXTGLOB


class WebAppAssets:
    def __init__(self, APP: Flask, assets: pathlib.Path) -> None:
        self.__filters = WebAssetFilters()
        self.__assets_mapping = dict()
        self.__static_url = APP.static_url_path

        self.__asset_copy_items: list[tuple[pathlib.Path, pathlib.Path]] = []
        self.__asset_render_items: list[tuple[pathlib.Path, pathlib.Path]] = []

        self.__asset_folder = assets
        self.__static_folder = pathlib.Path(APP.static_folder).resolve()

        self.__content_types = {
            "css": dict(
                extension="css",
                merge=self.__css_merge,
            ),
            "js": dict(
                extension="js",
                merge=self.__js_merge,
            ),
        }

    @staticmethod
    def __css_merge(css: list[str]):
        return "\n/* SEPARATE */\n".join(css)

    @staticmethod
    def __js_merge(js: list[str]):
        return "\n// SEPARATE\n".join(js)

    def __apply_filter(self, filter_names: list[str], content: str) -> str:
        for filter_name in filter_names:
            content = self.__filters.__getattribute__(filter_name.lower().strip())(
                content
            )
        return content

    def __asset_glob(
        self, globs
    ) -> Generator[tuple[pathlib.Path, pathlib.Path], None, None]:
        for pattern in globs:
            for match in wcmatch.WcMatch(
                str(self.__asset_folder), pattern, flags=GLOB_FLAGS
            ).match():
                path_match = pathlib.Path(match)
                if path_match.is_file():
                    yield path_match.resolve(), self.__static_folder.joinpath(
                        path_match.relative_to(self.__asset_folder)
                    )

    def build(self):
        if self.__static_folder.exists():
            shutil.rmtree(str(self.__static_folder))

        for pair in self.__asset_copy_items:
            pair[1].parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(*pair)

        for asset in self.__asset_render_items:
            self.__build_asset(**asset)

        env.path("COOKIELIST_STATE_FOLDER").joinpath(
            "assets.json"
        ).resolve().write_bytes(orjson.dumps(self.__assets_mapping))

    def copy_assets(self, *globs):
        self.__asset_copy_items.extend(
            list(path_pair for path_pair in self.__asset_glob(globs))
        )

    def add_asset(
        self,
        asset_id: str,
        *globs: str,
        content_type: str,
        output_file_name: pathlib.Path = None,
        content_filters: str = "copy",
    ):
        assets_paths = list(path_pair for path_pair in self.__asset_glob(globs))
        if not assets_paths:
            return None

        if not output_file_name and len(assets_paths) >= 2:
            output_file_path = self.__static_folder.joinpath(
                "+".join([path_pair[0].stem for path_pair in assets_paths])
                + f".merged.{self.__content_types[content_type]['extension']}"
            ).resolve()
        elif not output_file_name and len(assets_paths) <= 1:
            output_file_path = self.__static_folder.joinpath(
                assets_paths[0][0].name
            ).resolve()
        else:
            output_file_path = self.__static_folder.joinpath(output_file_name).resolve()

        self.__assets_mapping[asset_id.upper()] = [
            dict(
                time=time.time(),
                uri=f"{self.__static_url}/{output_file_path.relative_to(self.__static_folder)}",
                file=str(output_file_path),
            )
        ]

        self.__asset_render_items.append(
            dict(
                paths=assets_paths,
                content_type=content_type,
                output_file_path=output_file_path,
                content_filters=content_filters.split("|"),
            )
        )

    def __build_asset(
        self,
        paths,
        content_type: str,
        output_file_path: pathlib.Path,
        content_filters: list[str],
    ):
        asset_type = self.__content_types[content_type]

        contents = []
        for path_pair in paths:
            contents.append(
                self.__apply_filter(
                    content_filters, path_pair[0].read_text(encoding="utf-8")
                )
            )
        contents = asset_type["merge"](contents)

        output_file_path.parent.mkdir(exist_ok=True, parents=True)
        output_file_path.write_text(contents, encoding="utf-8")
