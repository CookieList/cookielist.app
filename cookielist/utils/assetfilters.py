import os
import pathlib

import cssmin
import htmlmin
import jsmin
import nodejs

NODE_BIN = str(
    pathlib.Path(nodejs.__file__).parent.joinpath(
        "node.exe" if os.name == "nt" else "bin/node"
    )
)
NODE_PM = str(
    pathlib.Path(nodejs.__file__).parent.joinpath(
        "npm.cmd"
        if os.name == "nt"
        else f"bin/node {pathlib.Path(nodejs.__file__).parent.joinpath('lib/node_modules/npm/bin/npm-cli.js')}"
    )
)

setattr(os.environ, "NODE_BIN", NODE_BIN)
setattr(os.environ, "NODE_PM", NODE_PM)
os.environ["NODE_BIN"] = NODE_BIN
os.environ["NODE_PM"] = NODE_PM

from javascript import require

_webapp = pathlib.Path(__file__).parent.parent.joinpath("webapp").resolve()


class WebAssetFilters:
    def __init__(self) -> None:
        self.__tailwind = require("tailwindcss", "3.4.1")
        self.__sass = require("sass", "1.69.7")
        self.__postcss = require("postcss", "8.4.35")

    def sass(self, input: str):
        return self.__sass.compileString(
            input,
            {
                "syntax": "indented",
                "style": "expanded",
                "loadPaths": [str(_webapp / "assets/sass")],
            },
        ).css

    def tailwind(self, input: str):
        return (
            self.__postcss(
                [
                    self.__tailwind(
                        {
                            "content": [
                                str(_webapp / "**/*.{jinja,html,sass,css,svg,js,py}")
                            ],
                            "theme": {
                                "screens": {
                                    "md": {"max": "768px"},
                                    "lg": {"min": "769px", "max": "1024px"},
                                    "xl": {"min": "1025px", "max": "1279px"},
                                    "2xl": {"min": "1280px", "max": "1535px"},
                                    "3xl": {"min": "1536px"},
                                }
                            },
                            "darkMode": "class",
                        }
                    )
                ]
            )
            .process(input, {"from": None})
            .css
        )

    def cssmin(self, input: str):
        return cssmin.cssmin(input)

    def jsmin(self, input: str):
        return jsmin.jsmin(input)

    def svgmin(self, input: str):
        return htmlmin.minify(input)

    def htmlmin(self, input: str):
        return htmlmin.minify(input)

    def copy(self, input: str):
        return input
