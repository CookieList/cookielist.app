from io import BytesIO
from time import time

import flask_compress
from flask import Flask, abort, request, send_file, g
from flask_cors import CORS
from cookielist.utils import WebAppLogger

from cookielist.badgeapp.model import CookielistBadge, db
from cookielist.badgeapp.response import ResponseFormats
from cookielist.environment import env
from cookielist.utils import JsonToken

app = Flask(__name__)
app.config["COMPRESS_MIMETYPES"] = [
    "image/svg+xml",
    "text/xml",
    "text/plain",
    "application/json",
    "text/html",
]
app.config["COMPRESS_BR_LEVEL"] = 10
app.config["SQLALCHEMY_POOL_RECYCLE"] = 299
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["FLASK_DEBUG"] = env.bool("FLASK_DEBUG")

if env.bool("COOKIELIST_USE_MYSQL"):
    pa_user = env.string('USER', env.string("PA_MYSQL_USERNAME", env.string("PA_USERNAME")))
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"mysql+mysqlconnector://{pa_user}:{env.string('PA_MYSQL_PASSWORD')}@{pa_user}.mysql.pythonanywhere-services.com/{pa_user}$default"
    )
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"

app.url_map.strict_slashes = False

flask_compress.Compress(app)
db.init_app(app)
CORS(app)

response = ResponseFormats()

with app.app_context():
    db.create_all()


@app.route("/<int:id>.<string:format>", methods=["GET"])
@app.route("/*/<int:id>.<string:format>", methods=["GET"])
def get(id: int, format: str):
    data: CookielistBadge = db.session.query(CookielistBadge).get(id)

    if format.lower() not in response.MIMETYPES or data is None:
        return abort(404)

    result = response.get(data, format, request.args.to_dict(flat=True))

    if request.url_rule.rule.startswith("/*/"):
        return {
            "response": result.decode() if isinstance(result, bytes) else result,
            "options": response.get_svg_options(
                request.args.get(
                    "template", env.string("COOKIELIST_DEFAULT_BADGE_TEMPLATE")
                )
            ),
            "id": id,
            "format": format,
        }

    return send_file(
        BytesIO(result.encode() if isinstance(result, str) else result),
        mimetype=response.MIMETYPES[format],
        download_name=f"{data.anilist_username.lower()}.{id}.cookielist.{format}",
        max_age=5 * 60,
    )


@app.route("/<int:id>", methods=["POST"])
def post(id: int):
    update: dict = request.get_json(force=True)

    data: CookielistBadge = db.session.query(CookielistBadge).get(id)

    if data is None:
        data = CookielistBadge.create_badge(update)
        db.session.add(data)
    else:
        try:
            if int(JsonToken.decode(update["__token"])["__id"]) != int(
                update["anilist_user_id"]
            ):
                return {
                    "id": id,
                    "success": False,
                }
        except Exception:
            return {
                "id": id,
                "success": None,
            }
        data.update_badge(update)
    db.session.commit()

    return {
        "id": id,
        "success": True,
    }


@app.before_request
def before_request():
    g.request_start_time = time()


@app.after_request
def after_request_func(response):
    if env.bool("RESPONSE_LOGGER"):
        WebAppLogger.make_request_log(response)
    if env.bool("STATISTICS_LOGGER"):
        WebAppLogger.make_badge_log(response)
    response.headers.add("Access-Control-Allow-Origin", "*")
    response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
    response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS")
    return response
