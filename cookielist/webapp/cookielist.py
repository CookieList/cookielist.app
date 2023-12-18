import datetime
import zoneinfo
from pathlib import Path

import flask_compress
import flask_debugtoolbar
import humanfriendly
from flask import Flask, render_template
from jinja2_env import EnvExtension
# from jinja2_humanize_extension import HumanizeExtension
# from jinja_markdown import MarkdownExtension

from cookielist.utils import WebAppAssets, WebAppJinjaTags
from cookielist.environment import env
from cookielist.webapp import endpoints

app = Flask(
    "cookielist",
    static_url_path="",
    static_folder=env.path("COOKIELIST_STATE_FOLDER").joinpath("assets"),
    template_folder=Path(__file__).parent.joinpath("templates"),
)

flask_compress.Compress(app)

app.url_map.strict_slashes = False
app.config["MAX_CONTENT_LENGTH"] = 1024 * 1024 * 10  # 10MB
app.config["SECRET_KEY"] = env["FLASK_APP_SECRET"]
app.config["PERMANENT_SESSION_LIFETIME"] = datetime.timedelta(days=365)
app.config["SESSION_COOKIE_SECURE"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_NAME"] = "session"
app.config["COMPRESS_MIMETYPES"] = [
    "image/svg+xml",
    "text/html",
    "text/css",
    "text/xml",
    "application/json",
    "application/javascript",
]
app.config["COMPRESS_BR_LEVEL"] = 6
if env.bool("FLASK_DEBUG"):
    app.config["DEBUG"] = True
    app.config["EXPLAIN_TEMPLATE_LOADING"] = True
    app.config["TEMPLATES_AUTO_RELOAD"] = True
    app.config["DEBUG_TB_PROFILER_ENABLED"] = True
    app.config["DEBUG_TB_TEMPLATE_EDITOR_ENABLED"] = True
    flask_debugtoolbar.DebugToolbarExtension(app)


asset = WebAppAssets(app, Path(__file__).parent.joinpath("assets"))
asset.copy_assets("images/*.*", "images/**/*.*", "fonts/*.*", "graphql/*.*", "*.*")
asset.add_asset(
    "SASS",
    "sass/*.sass",
    content_type="css",
    content_filters="sass | tailwind | cssmin",
)
asset.add_asset(
    "JS",
    "javascript/*.js",
    "javascript/**/*.js",
    content_type="js",
    content_filters="jsmin",
)

app.jinja_env.add_extension(WebAppJinjaTags.IconTag)
app.jinja_env.add_extension(WebAppJinjaTags.WebAssetContainerTag)
# app.jinja_env.add_extension(MarkdownExtension)
# app.jinja_env.add_extension(HumanizeExtension)
app.jinja_env.add_extension(EnvExtension)
app.jinja_env.add_extension(WebAppJinjaTags.BadgeSnippet)

app.jinja_env.globals.update(
    dict(
        human=humanfriendly,
        static=WebAppJinjaTags.static_resource_read,
        any=any,
        SITE_NAME=env.string("WEBAPP_NAME"),
        COOKIEDB_VERSION="1234939792",
        TZINFO=sorted(zoneinfo.available_timezones()),
        ADMIN_ID=env.string("ANILIST_DEV_ID"),
        CL_USERNAME=env["CL_USERNAME"],
        CL_PASSWORD=env["CL_PASSWORD"],
        CL_ADMIN_TOKEN=env["CL_ADMIN_TOKEN"],
    )
)

endpoints.UserPageView.register(app)
endpoints.BadgeView.register(app)
endpoints.ApiView.register(app)
endpoints.AboutView.register(app)
endpoints.AdminView.register(app)

if not app.debug:  # TODO

    @app.errorhandler(Exception)
    def error(error):
        CODE = 500 if not hasattr(error, "code") else error.code
        NAME = f"Server Error: {error}" if not hasattr(error, "name") else error.name
        return (
            render_template(
                "error.jinja",
                error=dict(code=CODE, name=NAME),
            ),
            CODE,
        )

else:
    asset.build()
