import time

from flask import abort, request, send_file
from flask_classful import FlaskView, route

from cookielist.badge import BadgeTemplates
from cookielist.utils import BadgeCacheHandler
from cookielist.utils.storage import storage

badge_cdn = BadgeCacheHandler()


class BadgeView(FlaskView):
    route_base = "/"
    default_methods = ["GET"]

    _templates = BadgeTemplates()

    @route("/<int:id>.svg")
    def get_badge(self, id):
        data = badge_cdn.get(id)
        if data is None:
            return abort(404)
        data.update(request.args)
        svg_image = self._templates.render_to_io(
            request.args.get("template", "default"), **data
        )

        if request.referrer:
            if request.referrer.startswith("https://anilist.co/"):
                storage[id] = int(time.time())

        return send_file(
            svg_image,
            mimetype="image/svg+xml",
            download_name=f"{data['name']}.{id}.cookielist.badge.svg",
            max_age=5,
        )

    @route("/<int:id>.json")
    def get_badge_data(self, id):
        return badge_cdn.get(id) or abort(404)
