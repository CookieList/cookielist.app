import re
from collections import ChainMap
from uuid import uuid4

import arrow
import jsonurl_py as jsonurl
from itsdangerous import BadSignature, URLSafeSerializer

from cookielist.environment import env

_serializer = URLSafeSerializer(env.list("COOKIELIST_TOKEN_KEYS"))
_regex = re.compile(r"\[//\]:\s<>\s\(cookielist:(.*?)\)")
_options = jsonurl.CommonOpts(
    implied_list=False,
    implied_dict=True,
    distinguish_empty_list_dict=True,
    aqf=False,
)


def encode(data: dict, salt: str = "", _format: str = "{}") -> str:
    data[str(uuid4())] = str(uuid4())
    data["__created"] = arrow.utcnow().isoformat()
    return _format.format(
        _serializer.dumps(data, salt=env.string("COOKIELIST_TOKEN_SALT") + str(salt))
    )


def decode(data: str, salt: str = "") -> dict:
    try:
        return _serializer.loads(
            data, salt=env.string("COOKIELIST_TOKEN_SALT") + str(salt)
        )
    except BadSignature:
        return {}


def url_encode(data: dict) -> str:
    return jsonurl.dumps(data, opts=_options)


def url_decode(data: str) -> str:
    return jsonurl.loads(data, opts=_options)


def find_and_decode(data: str, regex: re.Pattern = _regex) -> dict:
    return dict(ChainMap(*[url_decode(match) for match in regex.findall(data)]))
