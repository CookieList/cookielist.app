from flask import stream_template
from flask_classful import FlaskView, route


class UserPageView(FlaskView):
    route_base = "/"
    default_methods = ["GET"]

    @route("/<int:id>")
    def user_page(self, id):
        return stream_template("endpoints/user.jinja", id=id)
