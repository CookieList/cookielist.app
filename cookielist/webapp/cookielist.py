import datetime
import uuid
import zoneinfo
from pathlib import Path
from time import time
import flask_minify

import flask_compress
import flask_debugtoolbar
import humanfriendly
import orjson
from flask import Flask, g, render_template, session, abort, request
from flask.json.provider import JSONProvider
from flask_cors import CORS
from jinja2_env import EnvExtension
from rich.console import Console

from cookielist.badge import TEMPLATES
from cookielist.environment import env
from cookielist.utils import WebAppAssets, WebAppJinjaTags, WebAppLogger
from cookielist.webapp import endpoints


class ORJSONProvider(JSONProvider):
    def __init__(self, *args, **kwargs):
        self.options = kwargs
        super().__init__(*args, **kwargs)

    def loads(self, s, **kwargs):
        return orjson.loads(s)

    def dumps(self, obj, **kwargs):
        return orjson.dumps(obj, option=orjson.OPT_NON_STR_KEYS).decode("utf-8")


app = Flask(
    "cookielist",
    static_url_path="/static",
    static_folder=env.path("COOKIELIST_STATE_FOLDER").resolve().joinpath("assets"),
    template_folder=Path(__file__).parent.joinpath("templates"),
)

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
else:
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = datetime.timedelta(days=7)

flask_compress.Compress(app)
CORS(app, origins=env.list("COOKIELIST_BADGE_SERVERS"))
flask_minify.Minify(app)
app.json = ORJSONProvider(app)

if env.bool("FLASK_DEBUG"):
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
app.jinja_env.add_extension(EnvExtension)
app.jinja_env.policies["json.dumps_function"] = (
    lambda dictionary, **kwargs: orjson.dumps(dictionary).decode()
)

app.jinja_env.globals.update(
    dict(
        human=humanfriendly,
        static=WebAppJinjaTags.static_resource_read,
        any=any,
        env=env,
        SITE_NAME=env.string("WEBAPP_NAME"),
        COOKIEDB_VERSION="1234939792",
        TZINFO=sorted(zoneinfo.available_timezones()),
        BADGE_TEMPLATES=TEMPLATES,
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


@app.before_request
def before_request():
    if env.bool("RESPONSE_LOGGER"):
        WebAppLogger.make_request_log()

    g.request_start_time = time()

    cookie_user_id = session.get("id", default=None)
    cookie_user_session = session.get("session", default=None)

    if cookie_user_session is None:
        if cookie_user_id is not None:
            session["session"] = str(cookie_user_id)
        else:
            session["session"] = "anonymous-" + str(uuid.uuid4()).replace("-", "")

    g.session_id = session["session"]

    if env.bool("COOKIELIST_DEBUG") and env.string(
        "COOKIELIST_DEBUG_PASSWORD"
    ) != session.get("__debug_password__", ""):
        if request.endpoint not in [
            "static",
            "AdminView:access_debug_mode",
            "AboutView:favicon_ico",
            "AboutView:robots_txt",
        ]:
            return
            return abort(401)


@app.after_request
def after_request_func(response):
    if env.bool("RESPONSE_LOGGER"):
        WebAppLogger.make_request_log(response)
    if env.bool("STATISTICS_LOGGER"):
        WebAppLogger.make_stats_log(response)
    return response


def error(error):
    error_code = 500 if not hasattr(error, "code") else error.code
    error_name = f"Server Error: {error}" if not hasattr(error, "name") else error.name
    trace_id = str(uuid.uuid4()).replace("-", "")
    trace_title = f"{error_name} ({error_code}) [ID:{trace_id}]"[-100:]

    console = Console(record=True, width=100)
    with console.capture() as capture:
        console.print_exception(show_locals=False, width=100)
        exception_svg = console.export_svg(title=trace_title, clear=False)
        exception_text = f"{trace_title: ^100}\n" + console.export_text(clear=False)

    if env.bool("STATISTICS_LOGGER"):
        if not env.bool("COOKIELIST_DEBUG"):
            console = Console(record=True, width=100)
            with console.capture() as capture:
                console.print_exception(show_locals=False, width=100)
        WebAppLogger.make_traceback_log(
            f"{trace_title: ^100}\n" + console.export_text(), trace_id=trace_id
        )

    return (
        render_template(
            "error.jinja",
            error=dict(
                error_code=error_code,
                error_name=error_name,
                exception_svg=exception_svg,
                exception_text=exception_text,
                trace_id=trace_id,
            ),
        ),
        error_code,
    )


app.register_error_handler(Exception, error)
app.register_error_handler(500, error)

if app.debug:
    asset.build()
