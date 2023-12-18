from flask import render_template, request
from flask_classful import FlaskView, route

from cookielist.utils import BadgeCacheHandler

badge_cdn = BadgeCacheHandler()


class UserPageView(FlaskView):
    route_base = "/"
    default_methods = ["GET"]

    @route("/<int:id>")
    def user_page(self, id):
        user = request.args.get("_", None) or badge_cdn.get(id, {"name": None})["name"]
        return render_template("endpoints/user.jinja", user=user, id=id)
