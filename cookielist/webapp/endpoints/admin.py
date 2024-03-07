import platform
import re
import shutil
import socket
import uuid
from functools import wraps
from pathlib import Path

import psutil
import py7zr
from arrow import Arrow
from flask import abort, request, session
from flask_classful import FlaskView, route
from pympler import asizeof

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

    def fail(self):
        return str(1 / 0)

    @route("synchronize", methods=["POST"])
    @authorize
    def synchronize(self):
        path = Path(f"/home/{env.string('PA_USERNAME')}/app/.synchronize.archive.7z")
        if path.is_file():
            state = Path(env.string("COOKIELIST_STATE_FOLDER")).resolve()
            if state.exists():
                shutil.rmtree(str(state), ignore_errors=True)
            with py7zr.SevenZipFile(path, "r") as archive:
                archive.extractall(path.parent)
            path.unlink()
            try:
                Path(request.args["state"]).rename(state)
            except Exception:
                pass
            return dict(status=True)
        return abort(400)

    # @authorize
    # def in_memory_badges_size(self):
    #     badge_cdn = BadgeCacheHandler()

    #     byte_to_mb = 1048576
    #     size_in_bytes = asizeof.asizeof(badge_cdn)
    #     size_in_mb = size_in_bytes / byte_to_mb

    #     user_list_html = "".join(map(lambda _: f"<li>{_}</li>", badge_cdn.cache_items))

    #     return dict(
    #         json=dict(
    #             size_bytes=size_in_bytes,
    #             size_megabytes=size_in_mb,
    #             badge_count_in_cache=badge_cdn.cache_count,
    #             badge_user_ids=badge_cdn.cache_items,
    #         ),
    #         html=f"""<!--html-->
    #             <span class="italic font-bold text-lg text-slate-300">In memory size of { round(size_in_mb, 2) }MB with { badge_cdn.cache_count } badges.</span>
    #             <br class="m-2">
    #             <ol class="list-decimal list-inside text-sm italic">{ user_list_html }</ol>
    #         """,
    #     )

    @authorize
    def about_system_statistics(self):
        boot_time = Arrow.fromtimestamp(psutil.boot_time())
        network_counter = psutil.net_io_counters()

        return dict(
            json=dict(
                system=platform.uname()._asdict()
                | dict(
                    ip=socket.gethostbyname(socket.gethostname()),
                    mac=":".join(re.findall("..", "%012x" % uuid.getnode())),
                    host=socket.gethostname(),
                ),
                boot=dict(
                    formatted=boot_time.for_json(),
                    timestamp=boot_time.float_timestamp,
                    humanize=boot_time.humanize(),
                ),
                cpu=dict(
                    physical=psutil.cpu_count(logical=False),
                    total=psutil.cpu_count(logical=True),
                    frequency=dict(
                        map(
                            lambda _: (_[0], f"{_[1]}Mhz"),
                            psutil.cpu_freq()._asdict().items(),
                        )
                    ),
                    usage=dict(
                        total=f"{psutil.cpu_percent()}%",
                        cores=dict(
                            map(
                                lambda _: (str(_[0]), f"{_[1]}%"),
                                enumerate(
                                    psutil.cpu_percent(percpu=True, interval=1), start=1
                                ),
                            )
                        ),
                    ),
                ),
                memory=dict(
                    map(
                        lambda _: (
                            (_[0], f"{round(_[1] / 1024**3, 2)}GB")
                            if _[0] != "percent"
                            else (_[0], f"{_[1]}%")
                        ),
                        psutil.virtual_memory()._asdict().items(),
                    )
                ),
                swap=dict(
                    map(
                        lambda _: (
                            (_[0], f"{round(_[1] / 1024**3, 2)}GB")
                            if _[0] != "percent"
                            else (_[0], f"{_[1]}%")
                        ),
                        psutil.swap_memory()._asdict().items(),
                    )
                ),
                network=dict(
                    data=dict(
                        sent=f"{round(network_counter.bytes_sent / 1024**3, 2)}GB",
                        received=f"{round(network_counter.bytes_recv / 1024**3, 2)}GB",
                    ),
                    packets=dict(
                        sent=network_counter.packets_sent,
                        received=network_counter.packets_recv,
                    ),
                ),
            )
        )
