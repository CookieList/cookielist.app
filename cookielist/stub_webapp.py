from pathlib import Path

import py7zr
from flask import Flask, abort, render_template_string, send_file, request

from cookielist.assets import assets
from cookielist.environment import env

stub = Flask("cookielist-stub")


@stub.route("/", methods=["GET"])
@stub.route("/<path:path>", methods=["GET"])
def stub_catchall(path="/"):
    return render_template_string(
        assets["stub.jinja"].read_text(),
        site_name=env.string("WEBAPP_NAME"),
        gh_user=env.string("GH_USERNAME"),
        gh_repo=env.string("GH_REPO"),
    )


@stub.route("/favicon.ico", methods=["GET"])
def stub_favicon():
    return send_file(assets["favicon.ico"])


@stub.route("/_/synchronize", methods=["POST"])
def stub_synchronize():
    json: dict = request.get_json(force=True)
    path = Path(f"/home/{env.string('PA_USERNAME')}/app/.synchronize.archive.7z")
    if (
        json.get("CL_USERNAME") == env["CL_USERNAME"]
        and json.get("CL_PASSWORD") == env["CL_PASSWORD"]
        and json.get("CL_ADMIN_TOKEN") == env["CL_ADMIN_TOKEN"]
    ):
        if path.is_file():
            with py7zr.SevenZipFile(path, "r") as archive:
                archive.extractall(path.parent)
            path.unlink()
            return dict(status=True)
        return abort(400)
    else:
        return abort(401)
