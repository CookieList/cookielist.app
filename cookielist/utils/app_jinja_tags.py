import re
from functools import cache
from urllib.parse import quote

import heroicons
import orjson
from jinja2_simple_tags import ContainerTag, StandaloneTag

from cookielist.environment import env

CLF = env.path("COOKIELIST_STATE_FOLDER")


class WebAssetContainerTag(ContainerTag):
    tags = {"assets"}
    _ASSET_MAP = None
    _TAG_REGEX = re.compile("\$([A-Z_]+)")

    def render(self, ID, caller: str = ""):
        if self._ASSET_MAP is None:
            mappings = CLF.joinpath("assets.json")
            if mappings.exists():
                self._ASSET_MAP = orjson.loads(mappings.read_bytes())
            else:
                self._ASSET_MAP = {}

        ID = str(ID).strip()
        content = str(caller())
        render = list()

        for asset in self._ASSET_MAP[ID]:
            variables = dict(
                ASSET_URL=asset["uri"],
                ASSET_FILE=str(asset["file"]),
                TIME=str(asset["time"]),
            )
            render.append(
                self._TAG_REGEX.sub(
                    lambda match, variables=variables: variables.get(
                        match.group(1).strip(), "/404"
                    ),
                    content,
                )
            )
        return "".join(render)


class IconTag(StandaloneTag):
    safe_output = True
    tags = {"icon"}

    def render(self, name, *, size=None, datauri=False, **kwargs):
        try:
            image = heroicons._render_icon("outline", name, size=size, **kwargs)
        except heroicons.IconDoesNotExist:
            options = list(
                f'{key.replace("_", "-")}="{value}"' for key, value in kwargs.items()
            ) + [(f'width="{size}" height="{size}"' if size is not None else "")]

            image = (
                CLF.joinpath("assets", name)
                .read_text()
                .replace(
                    "<svg",
                    "<svg " + " ".join(options),
                    1,
                )
                .replace(' xmlns="http://www.w3.org/2000/svg"', "", 1)
            )
        if datauri:
            if not "xmlns=" in image:
                image = image.replace("<svg", "<svg xmlns='http://www.w3.org/2000/svg'")
            encoded = (
                quote(image.replace('"', "'").replace("\n", ""))
                .replace("%20", " ")
                .replace("%27", "'")
                .replace("%3D", "=")
            )
            return "data:image/svg+xml," + encoded
        return image


@cache
def static_resource_read(filename):
    return CLF.joinpath("assets", filename).read_text()
