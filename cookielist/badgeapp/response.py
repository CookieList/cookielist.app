import base64
import re

import orjson

from cookielist.badge import BadgeTemplates
from cookielist.badgeapp.model import CookielistBadge
from cookielist.environment import env

BADGE = BadgeTemplates()


class ResponseFormats:
    MIMETYPES = {
        "json": "application/json",
        "html": "text/html",
        "svg": "image/svg+xml",
        "txt": "text/plain",
        "base64-uri": "text/plain",
        "xml-uri": "text/plain",
    }
    URI_REPLACE = {
        "\r": "%0D",
        "\n": "%0A",
        "%": "%25",
        "#": "%23",
        "(": "%28",
        ")": "%29",
        "<": "%3C",
        ">": "%3E",
        "?": "%3F",
        "[": "%5B",
        "\\": "%5C",
        "]": "%5D",
        "^": "%5E",
        "`": "%60",
        "{": "%7B",
        "|": "%7C",
        "}": "%7D",
    }
    URI_REPLACE_REGEX = re.compile(r"(?P<char>[\r\n%#()<>?[\\\]^`{|}])")

    def get(
        self, data: CookielistBadge, format: str = "json", arguments: dict = {}
    ) -> bytes:
        if format.lower() not in self.MIMETYPES:
            format = "json"
        content = getattr(self, f"_{format.replace('-', '_').lower()}")(
            data, **arguments
        )
        return content.encode() if isinstance(content, str) else content

    @staticmethod
    def get_svg_options(template: str = None):
        if not template:
            template = BADGE.defaultTemplate
        return BADGE.options(template)

    @staticmethod
    def _json(_data: CookielistBadge, **kwargs):
        json = _data.to_dict()
        json["anilist_avatar_image"] = _data.anilist_avatar_base_64()
        return orjson.dumps(json)

    @staticmethod
    def _svg(_data: CookielistBadge, **kwargs):
        template = kwargs.pop(
            "template", env.string("COOKIELIST_DEFAULT_BADGE_TEMPLATE")
        )
        return BADGE.render(
            template,
            **_data.to_dict()
            | {"anilist_avatar_base_64": _data.anilist_avatar_base_64}
            | kwargs,
        )

    def _base64_uri(self, _data: CookielistBadge, **kwargs):
        return "data:image/svg+xml;base64," + base64.encodebytes(
            self._svg(_data, **kwargs).encode()
        ).decode().replace("\n", "")

    def _xml_uri(self, _data: CookielistBadge, **kwargs):
        return "data:image/svg+xml," + self.URI_REPLACE_REGEX.sub(
            lambda match: self.URI_REPLACE.get(match[0], match[0]),
            self._svg(_data, **kwargs),
        )

    def _txt(self, _data: CookielistBadge, **kwargs):
        return self._svg(_data, **kwargs)

    @staticmethod
    def _html(_data: CookielistBadge, **kwargs):
        return "NOT YET IMPLEMENTED"
