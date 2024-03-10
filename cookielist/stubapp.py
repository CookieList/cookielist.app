import shutil
from pathlib import Path

import py7zr
from flask import Flask, abort, render_template_string, request, send_file, redirect, url_for
from cookielist.utils import WebAppLogger
from cookielist.assets import asset
from cookielist.environment import env

app = Flask("cookielist-stub")


@app.route("/", methods=["GET"])
@app.route("/<path:path>", methods=["GET"])
def stub_catchall(path="/"):
    return redirect(url_for("stub_page"))

@app.route("/favicon.ico", methods=["GET"])
def stub_favicon():
    return send_file(asset.path("favicon.ico"))

@app.route("/_/cookielist-stub", methods=["GET"])
def stub_page():
    return render_template_string(
        asset.content("stub.jinja"),
        site_name=env.string("WEBAPP_NAME"),
        gh_user=env.string("GH_USERNAME"),
        gh_repo=env.string("GH_REPO"),
    )


@app.route("/_/synchronize", methods=["POST"])
def stub_synchronize():
    json: dict = request.get_json(force=True)
    path = Path(f"/home/{env.string('PA_USERNAME')}/app/.synchronize.archive.7z")
    state = Path(env.string("COOKIELIST_STATE_FOLDER")).resolve()
    if (
        json.get("CL_USERNAME") == env["CL_USERNAME"]
        and json.get("CL_PASSWORD") == env["CL_PASSWORD"]
        and json.get("CL_ADMIN_TOKEN") == env["CL_ADMIN_TOKEN"]
    ):
        if path.is_file():
            if state.exists():
                shutil.rmtree(str(state), ignore_errors=True)
            with py7zr.SevenZipFile(path, "r") as archive:
                archive.extractall(path.parent)
            path.unlink()
            try:
                Path(request.args["state"]).rename(state)
            except Exception:
                pass
            return dict(status=True)
        return abort(400)
    else:
        return json #abort(401)


@app.after_request
def after_request_func(response):
    if env.bool("RESPONSE_LOGGER"):
        WebAppLogger.make_request_log(response)
    return response
        
cookielist_stub = app