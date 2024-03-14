import html
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
from flask import abort, request, session, url_for, redirect
from flask_classful import FlaskView, route, method

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
        path = Path(f"/home/{env.string('PA_USERNAME')}/{env.string('PA_SOURCE_FOLDER')}/.synchronize.archive.7z")
        if path.is_file() and path.exists():
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

    def ping(self):
        return dict(
            json=dict(status=True),
            html=f"""<!--html-->
            <div class="flex flex-col items-center justify-center w-full m-1">
                <img class="rounded-full w-1/3 p-1 md:w-1/2" src="{ url_for('static', filename='images/pong.png') }"/>
                <span class="text-xl m-1 font-bold italic">#PONG</span>
            </div>
            """,
        )

    @method("get")
    @method("post")
    @method("delete")
    def access_debug_mode(self):
        if request.method == "DELETE":
            session.pop("__debug_password__", None)
            return redirect("/")
        elif request.method == "GET":
            password = request.args.get("password", "").strip()
            if env.string("COOKIELIST_DEBUG_PASSWORD") == password:
                session["__debug_password__"] = password
            return redirect("/")
        elif request.method == "POST":
            password = request.get_json(force=True).get("password", "").strip()
            correct = env.string("COOKIELIST_DEBUG_PASSWORD") == password
            return dict(
                json=dict(password=password, correct=correct),
            )

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
        
    @route("/_/cookielist-stub", methods=["GET"])
    def cookielist_stub_redirect(self):
        return redirect(url_for('AboutView:index'))
