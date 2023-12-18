import base64
import mimetypes
import re
from functools import cache, partial
from io import BytesIO
from pathlib import Path
from urllib.parse import quote

import liquid
import minify_html
import orjson
import requests


class BadgeTemplates:
    def __init__(
        self,
        badge_directory: Path = Path(__file__).parent.joinpath("templates"),
        default_template: str = "default",
    ) -> None:
        self.__dir = badge_directory
        self.__templates: dict[str, liquid.BoundTemplate] = {}
        self.__template_default = default_template
        self.__current_template: str | None = None
        self.__plausible_match_regex = re.compile(
            r"""
            url\("(.*?)"\)|         # url("$0")
            url\('(.*?)'\)|         # url('$0')
            url\((.*?)\)|           # url($0)
            '(.*?)'|                # '$0'
            "(.*?)"                 # "$0"
            """,
            flags=re.VERBOSE,
        )
        self.__remove_tag_regex = re.compile(
            r"""<(script|liquid).*?(/>|</\1>)""", flags=re.DOTALL
        )

        self.__minify = partial(
            minify_html.minify,
            minify_css=True,
            minify_js=True,
            remove_processing_instructions=True,
        )

        self.environment = liquid.Environment(
            tolerance=liquid.Mode.LAX,
            undefined=liquid.Undefined,
            strict_filters=False,
            loader=None,
        )

        self.__load_badges(self.__dir)

    def render(self, template: str, **kwargs) -> str:
        self.__current_template = (
            template if template.lower() in self.__templates else None
        )
        svg_template = self.__templates.get(
            template.lower(), self.__templates[self.__template_default]
        )
        return svg_template.render(data=kwargs)

    def render_to_io(self, template: str, **kwargs) -> BytesIO:
        return BytesIO(self.render(template, **kwargs).encode())

    def __load_badges(self, badge_directory: Path):
        self.__templates.update(
            {
                template.parent.stem: self.environment.from_string(
                    self.__render_template(template.parent),
                    name=template.name,
                    path=template,
                )
                for template in badge_directory.glob("*/__badge__.svg")
            }
        )

    def __render_template(self, badge: Path):
        return self.__generate_template(
            self.__remove_tag_regex.sub(
                "", badge.joinpath("__badge__.svg").read_text(encoding="utf-8")
            )
        )

    def __generate_template(self, string: str) -> str:
        return self.__plausible_match_regex.sub(self.__substitute_regex_match, string)

    @staticmethod
    @cache
    def __is_mime_binary(mime_type: str) -> bool:
        return (
            False
            if mime_type.split("/")[0] == "text"
            or mime_type
            in ["application/json", "image/svg-xml", "application/javascript"]
            else True
        )

    @staticmethod
    @cache
    def __get_mime_type(url: str | Path) -> str:
        guessed_type = mimetypes.guess_type(url)[0]
        mime_type = (
            "text/css"
            if str(url).startswith("https://fonts.googleapis.com/css")
            else guessed_type
            if guessed_type
            else "application/octet-stream"
        )
        return mime_type

    @cache
    def __validated_match(self, string_match: str) -> str | Path | None:
        if not string_match:
            return None
        if (
            string_match.startswith("https://") or string_match.startswith("http://")
        ) and "//www.w3.org" not in string_match:
            return string_match
        try:
            asset_path = self.__dir.joinpath(
                self.__current_template or self.__template_default, string_match
            )
            if asset_path.exists() and asset_path.is_file():
                return asset_path.resolve()
        except Exception:
            pass

    def __read_data(self, url: str | Path) -> str | bytes:
        mimetype = self.__get_mime_type(url)
        binary = self.__is_mime_binary(mimetype)

        if isinstance(url, str):
            data = requests.get(url)
            return data.content if binary else self.__minify_data(data.text, mimetype)
        else:
            return (
                url.read_bytes()
                if binary
                else self.__minify_data(url.read_text(encoding="utf-8"), mimetype)
            )

    @staticmethod
    def __xml_crop(data: str, tag: str) -> str:
        return data[len(tag) + 2 : -len(tag) - 3]

    def __minify_data(self, data: str, mimetype: str) -> str:
        if mimetype == "text/css":
            data = self.__xml_crop(
                self.__minify(
                    f"<style>{data}</style>",
                ),
                "style",
            )

        elif mimetype == "application/javascript":
            data = self.__xml_crop(
                self.__minify(
                    f"<script>{data}</script>",
                ),
                "script",
            )

        elif mimetype == "application/json":
            data = orjson.dumps(orjson.loads(data)).decode()

        elif mimetype == "image/svg-xml":
            data = self.__minify(data)

        return data

    def __create_data_uri(self, data: str | bytes, mimetype: str) -> str:
        binary = self.__is_mime_binary(mimetype)
        charset = "us-ascii" if binary else "utf-8"
        url = (
            base64.encodebytes(data.encode() if isinstance(data, str) else data)
            .decode()
            .replace("\n", "")
            if binary
            else quote(data.decode() if isinstance(data, bytes) else data)
        )
        return f"data:{mimetype};charset={charset}{';base64' if binary else ''},{url}"

    def __uri_substitute(self, url: str | Path) -> str:
        mimetype = self.__get_mime_type(url)
        binary = self.__is_mime_binary(mimetype)

        try:
            data = self.__read_data(url)
        except Exception:
            data = "INVALID-DATA"
            binary = False

        if not binary:
            if not self.__has_substitutions(data):
                data_uri = self.__create_data_uri(data, mimetype)
            else:
                data_uri = self.__create_data_uri(
                    self.__generate_template(data), mimetype
                )
        else:
            data_uri = self.__create_data_uri(data, mimetype)

        return data_uri

    def __has_substitutions(self, string):
        return bool(
            list(
                self.__validated_match(group[0])
                for group in list(
                    match.groups()
                    for match in self.__plausible_match_regex.finditer(string)
                    if any(match.groups())
                )
            )
        )

    def __substitute_regex_match(self, match: re.Match):
        matched = list(filter(bool, match.groups()))
        matched = self.__validated_match("" if not matched else matched[0])

        if not matched:
            return match.group(0)
        else:
            subbed = f'"{self.__uri_substitute(matched)}"'
            if match.group(0).startswith("url"):
                subbed = f"url({subbed})"
            return subbed
