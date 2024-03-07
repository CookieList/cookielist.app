import pathlib

import dotted_dict
from flask import abort, request, session, stream_template, redirect
from flask_classful import FlaskView, route

from cookielist.badge import calculate_badge
from cookielist.environment import env
from cookielist.processors import _pre_process
from cookielist.processors.lists import ListProcessor
from cookielist.processors.queue import QueueProcessor
from cookielist.processors.schedule import ScheduleProcessor
from cookielist.utils import AnilistClient
from cookielist.utils import WebAppLogger

anilist = AnilistClient(
    pathlib.Path(__file__).parent.parent.parent.joinpath("assets", "register.graphql")
)


class ApiView(FlaskView):
    route_base = "/"

    _list = ListProcessor()
    _queue = QueueProcessor()
    _schedule = ScheduleProcessor()

    @route("/api", methods=["POST"])
    def process_data(self):
        Media, User, Options = _pre_process.process(request.get_json(force=True))

        parsedUserList = self._list.calculate(Media, User, Options)
        parsedUserSchedule = self._schedule.calculate(Media, User, Options)
        parsedUserQueue = self._queue.calculate(Media, User, Options)
        parsedUserBadge = calculate_badge(parsedUserList, User, Options)

        return stream_template(
            "endpoints/lists.jinja",
            userSchedule=parsedUserSchedule,
            userList=parsedUserList,
            userQueue=parsedUserQueue,
            userBadge=parsedUserBadge,
            userInfo=User,
            userOptions=Options,
        )

    @route("/register", methods=["GET", "POST"])
    def register_user(self):
        if request.method == "GET":
            return stream_template("endpoints/register.jinja")

        data = dotted_dict.DottedDict(request.get_json(force=True))

        if data.action == "login":
            response = anilist.query("UserInfo", authorization=data.token)["Viewer"]

            if response is None:
                return abort(500, "Invalid Grant Code")

            session["id"] = str(response["id"])
            session["name"] = response["name"]
            session["avatar"] = response["avatar"]["large"]
            session["token"] = data.token

            session.permanent = True
            session["session"] = str(response["id"])

            if env.bool("STATISTICS_LOGGER"):
                WebAppLogger.make_session_id_log(str(response["id"]))

            return {"status": "success"}

        elif data.action == "admin_login":
            status = (
                "success"
                if (
                    data.username == env["CL_USERNAME"]
                    and data.password == env["CL_PASSWORD"]
                    and data.key == env["CL_ADMIN_TOKEN"]
                )
                else "failed"
            )

            if status == "success":
                session["CL_USERNAME"] = str(data.username)
                session["CL_PASSWORD"] = str(data.password)
                session["CL_ADMIN_TOKEN"] = str(data.key)
                session.permanent = True
            return {"status": status}

        elif data.action == "logout":
            session.pop("id", None)
            session.pop("name", None)
            session.pop("avatar", None)
            session.pop("token", None)
            session.pop("CL_USERNAME", None)
            session.pop("CL_PASSWORD", None)
            session.pop("CL_ADMIN_TOKEN", None)
            return {"status": "success"}

        else:
            return abort(404)
        
    @route("/_/cookielist-stub", methods=["GET"])
    def cookielist_stub_redirect(self):
        return redirect("/")
    

    # @route("/settings_encode", methods=["POST"])
    # def encode_settings(self):
    #     data = request.get_json(force=True)
    #     _salt = request.args.get("id")
    #     _format = request.args.get("format") or "[//]: <> (cookielist:{})"
    #     if _salt is None:
    #         return abort(500)
    #     return JsonToken.encode(data, salt=_salt, _format=_format)
