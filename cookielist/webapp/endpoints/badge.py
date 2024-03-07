from flask import abort, redirect, request
from flask_classful import FlaskView, route

from cookielist.utils import BADGE_REDIRECT_SERVERS


class BadgeView(FlaskView):
    route_base = "/"
    default_methods = ["GET", "POST"]

    @route("/<int:id>.<string:format>")
    def badge_redirect(self, id, format):
        server = BADGE_REDIRECT_SERVERS.get(str(id)[0])
        if server is None:
            return abort(500)
        if request.method == "GET":
            return redirect(f"{request.scheme}://{server}/{id}.{format}", 301)
        elif request.method == "POST":
            return {
                "method": "POST",
                "url": f"{request.scheme}://{server}/{id}.{format}{'?' if request.args else ''}{request.query_string.decode()}",
            }
