from cookielist.environment import env
import pathlib

import dotted_dict
from flask import abort, render_template, request, session
from flask_classful import FlaskView, route

from cookielist.badge import BadgeManager
from cookielist.processors.lists import ListProcessor
from cookielist.processors.queue import QueueProcessor
from cookielist.processors.schedule import ScheduleProcessor
from cookielist.utils import AnilistClient

anilist = AnilistClient(
    pathlib.Path(__file__).parent.parent.parent.joinpath("assets", "register.graphql")
)
badge = BadgeManager()


class ApiView(FlaskView):
    route_base = "/"

    _list = ListProcessor()
    _queue = QueueProcessor()
    _schedule = ScheduleProcessor()

    @route("/api", methods=["POST"])
    def process_data(self):
        data = dotted_dict.DottedDict(request.get_json(force=True))
        result = self._list.calculate(data)
        badge_data = badge.update_badge_data(
            data.anime.data.MediaListCollection.user, result["result"]
        )
        schedule = self._schedule.calculate(data)
        queue = self._queue.calculate(data)

        return render_template(
            "endpoints/lists.jinja",
            schedule=schedule,
            data=result,
            user=data.anime.data.MediaListCollection.user,
            queue=queue,
            badge=badge_data,
        )

    @route("/register", methods=["GET", "POST"])
    def register_user(self):
        if request.method == "GET":
            return render_template("endpoints/register.jinja")

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
