# @route("/_access")
# def assess_logs(self):
#     storage.sync()
#     return storage

from functools import wraps
from pathlib import Path

import py7zr
from flask import abort, session, request
from flask_classful import FlaskView, route
from pympler import asizeof

from cookielist.utils import BadgeCacheHandler
from cookielist.environment import env


def authorize(route):
    @wraps(route)
    def authorization(*args, **kwargs):
        try:
            json_auth_data = request.get_json(force=True)
        except Exception:
            json_auth_data = dict()
        if (
            (
                session.get("CL_USERNAME")
                or request.args.get("CL_USERNAME")
                or json_auth_data.get("CL_USERNAME")
            )
            == env["CL_USERNAME"]
            and (
                session.get("CL_PASSWORD")
                or request.args.get("CL_PASSWORD")
                or json_auth_data.get("CL_PASSWORD")
            )
            == env["CL_PASSWORD"]
            and (
                session.get("CL_ADMIN_TOKEN")
                or request.args.get("CL_ADMIN_TOKEN")
                or json_auth_data.get("CL_ADMIN_TOKEN")
            )
            == env["CL_ADMIN_TOKEN"]
        ):
            return route(*args, **kwargs)
        else:
            return abort(401)

    return authorization


class AdminView(FlaskView):
    route_base = "/"
    route_prefix = "/_/"
    default_methods = ["GET"]

    @route("synchronize")
    @authorize
    def synchronize(self):
        path = Path(f"/home/{env.string('PA_USERNAME')}/app/.synchronize.archive.7z")
        if path.is_file():
            with py7zr.SevenZipFile(path, "r") as archive:
                archive.extractall(path.parent)
            path.unlink()
            return dict(status=True)
        return abort(400)

    @authorize
    def in_memory_badges_size(self):
        badge_cdn = BadgeCacheHandler()

        unit_name = "MB"
        byte_to_unit = 1048576
        unit_round = 2
        return dict(
            size=asizeof.asizeof(badge_cdn),
            size_formatted=f"{round(asizeof.asizeof(badge_cdn)/byte_to_unit, unit_round)} {unit_name}",
            cache_size=badge_cdn.cache_count,
            contents=badge_cdn.cache_items,
        )
