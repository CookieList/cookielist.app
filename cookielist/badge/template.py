import base64
import mimetypes
import re
import uuid
from functools import cache
from io import BytesIO
from pathlib import Path

import orjson
from jinja2 import (
    DebugUndefined,
    Environment,
    FileSystemLoader,
    Template,
    select_autoescape,
)
from jinja2_simple_tags import StandaloneTag

from cookielist.assets import asset
from cookielist.environment import env

templatesPath = Path(__file__).parent.joinpath("templates")
randomSalt = str(uuid.uuid4())
availableFonts: dict[str, str | dict[str, str]] = orjson.loads(
    asset.content("defaultFontSize.json", mode="binary")
)
svgPathNormalizeRegex = re.compile(r"\.\d+|\d+\.\d+|\d+")


class EmbedTag(StandaloneTag):
    tags = {"embed"}

    @cache
    def render(self, path: Path):
        path = templatesPath.joinpath(path)
        mime = mimetypes.guess_type(path)[0] or "application/octet-stream"
        if not path.exists() or not path.is_file():
            return ""
        return f"data:{mime};charset=us-ascii;base64," + base64.encodebytes(
            path.read_bytes()
        ).decode().replace("\n", "")


class TailwindTag(StandaloneTag):
    tags = {"tailwind_colors_css"}

    def render(self):
        return f"""<!--html--><style>/* TAILWINDCSS-COLOR-PALATE-CSS-{randomSalt} */</style>"""


class FontTag(StandaloneTag):
    tags = {"font_css"}

    def render(self):
        return f"""<!--html--><style>/* FONTS-CSS-{randomSalt} */</style>"""


def approximate_string_width(
    string: str = "",
    font: str = "victor-mono",
    size: float = availableFonts["victor-mono"]["factor"],
):
    if not string:
        return 0
    if font not in availableFonts:
        font = "victor-mono"

    unknown: float = availableFonts[font]["unknown"]
    characters: dict = availableFonts[font]["characters"]
    size = float(size)

    return sum([characters.get(letter, unknown) for letter in str(string)], 0) / (
        availableFonts[font]["factor"] / size
    )


def coordinate(cord: str):
    cord_ = cord.split(",")
    try:
        x = float(cord_[0])
        y = float(cord_[1])
    except ValueError:
        return {"x": 0, "y": 0}
    return {"x": x, "y": y}


def svg_path_normalize(path: str, normalize: int | float, original: int | float = 100):
    if float(normalize) <= 0:
        return ""
    factor = float(original) / float(normalize)
    return svgPathNormalizeRegex.sub(
        lambda match: str(float(match.group(0)) / factor),
        path,
    )


class BadgeTemplates:
    def __init__(self) -> None:
        self.defaultTemplate = env.string("COOKIELIST_DEFAULT_BADGE_TEMPLATE")
        self.templatesPath = templatesPath
        self.compressRegex = re.compile(r"(>)(\s+)(<)|(\s+)(/?>)|(<)(\s+)", re.DOTALL)
        self.environment = Environment(
            loader=FileSystemLoader(self.templatesPath),
            autoescape=select_autoescape(),
            auto_reload=env.bool("COOKIELIST_DEBUG"),
            undefined=DebugUndefined,
            extensions=[EmbedTag, TailwindTag, FontTag],
        )
        self.environment.globals.update(
            {
                "approximate_string_width": approximate_string_width,
                "coordinate": coordinate,
                "svg_path_normalize": svg_path_normalize,
            }
        )

        self.templates: dict[str, Template] = {
            template.lower()[:-14]: self.environment.get_template(template)
            for template in self.environment.list_templates()
            if template.lower().endswith("/__badge__.svg")
        }

        tailwindColors: dict[str, str | dict[str, str]] = orjson.loads(
            asset.content("tailwindColors.json", mode="binary")
        )
        self.tailwindColorsMap: dict[str, str] = dict(
            sum(
                [
                    (
                        [
                            (f"--color-{color}-{intensity}", shade)
                            for intensity, shade in shades.items()
                        ]
                        if isinstance(shades, dict)
                        else [(f"--color-{color}", shades)]
                    )
                    for color, shades in tailwindColors.items()
                ],
                [],
            )
        )
        self.tailwindColorsRegex = re.compile(
            rf"""(?P<variable>--color-(?P<color>{'|'.join(tailwindColors.keys())})(?:-(?P<intensity>950|900|800|700|600|500|400|300|200|100|50))?)""",
            re.IGNORECASE,
        )

        self.builtinFonts = availableFonts
        self.fontsRegex = re.compile(
            rf"""(?:font-family=(?:'|")(?P<font>{'|'.join(self.builtinFonts.keys())})(?:'|"))""",
            re.IGNORECASE,
        )

    def _substitute_color_palate_css(self, svgCode: str) -> str:
        usedColors = set(
            [match[0].lower() for match in self.tailwindColorsRegex.findall(svgCode)]
        )
        colorCss = f":root {{ {';'.join([f'{color}: {self.tailwindColorsMap.get(color)}' for color in usedColors])} }}"
        return svgCode.replace(
            f"/* TAILWINDCSS-COLOR-PALATE-CSS-{randomSalt} */", colorCss
        )

    @cache
    def _font_to_uri(self, font_file: str) -> str:
        return "data:application/font-woff;charset=utf-8;base64," + base64.encodebytes(
            templatesPath.joinpath("__assets__", "fonts", font_file).read_bytes()
        ).decode().replace("\n", "")

    def _substitute_font_css(self, svgCode: str) -> str:
        usedFonts = set([match.lower() for match in self.fontsRegex.findall(svgCode)])
        fontsCss = " ".join(
            [
                self.builtinFonts[font]["css"].format(
                    self._font_to_uri(self.builtinFonts[font]["file"])
                )
                for font in usedFonts
            ]
        )
        return svgCode.replace(f"/* FONTS-CSS-{randomSalt} */", fontsCss)

    def render(self, template_name: str, **kwargs: dict[str, str]):
        template = self.templates.get(
            template_name.lower(), self.templates[self.defaultTemplate]
        )
        _options = self.options(template_name)
        options = {opt["id"]: opt["default"] for opt in _options}
        options.update(kwargs)

        svg = (
            self._substitute_font_css(
                self._substitute_color_palate_css(template.render(_=options))
            )
            .strip()
            .replace("\n", "")
        )

        svg = self.compressRegex.sub(r"\1\3\5\6", svg)

        return svg

    def render_to_io(self, template_name: str, **kwargs: dict[str, str]):
        BytesIO(self.render(template_name, **kwargs).encode())

    @cache
    def _options(self, template_name: str):
        return orjson.loads(
            self.templatesPath.joinpath(template_name, "__options__.json").read_bytes()
        )

    def options(self, template_name: str) -> list[dict[str, str]]:
        return self._options(
            template_name if template_name in self.templates else self.defaultTemplate
        )
