from flask import redirect, url_for
from flask_classful import FlaskView, route

from cookielist.environment import env


class AboutView(FlaskView):
    route_base = "/"
    default_methods = ["GET"]

    @route("/")
    def index(self):
        return redirect(
            url_for("UserPageView:user_page", id=env.string("ANILIST_DEV_ID"))
        )
