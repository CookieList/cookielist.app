from email.policy import default
import logging
import re
import socket
import argparse
from typing import Callable
import warnings
from contextlib import suppress
from functools import partial
import arrow
from pathlib import Path
import time
from time import time as timestamp
import rich_click as click

import flask.cli
import werkzeug._reloader
from flask import Flask
from rich import print
from rich.panel import Panel
from rich.text import Text
from wcmatch import wcmatch
from wcmatch.pathlib import glob

from cookielist.environment import env

DEBUG = env.bool("COOKIELIST_DEBUG")
STATE_FOLDER = env.path("COOKIELIST_STATE_FOLDER")
REQUIRE_RELOAD_FILES = wcmatch.WcMatch(
    str(Path(__file__).parent),
    f"*.@(jinja|sass|html|js|graphql|json|txt|css|svg)",
    flags=wcmatch.RECURSIVE | glob.EXTGLOB,
).match()
_COOKIELIST_APP = ""
_COOKIELIST_APP_THEME = ""


class _ReloaderLoop(werkzeug._reloader.WatchdogReloaderLoop):
    __cookielist_last_reload_timestamp = float("-inf")

    def restart_with_reloader(self) -> int:
        with suppress(OSError):
            werkzeug._reloader.WatchdogReloaderLoop.restart_with_reloader(self)

    def log_reload(self, filename: str):
        if timestamp() > self.__cookielist_last_reload_timestamp + 2:
            _log("[bold magenta]APP RELOADING...[/]")
            self.__cookielist_last_reload_timestamp = timestamp()


def _log(message: str):
    global _COOKIELIST_APP_THEME
    print(
        Panel(
            Text.from_markup(message, justify="center"),
            border_style=_COOKIELIST_APP_THEME,
            title=Text.from_markup(_COOKIELIST_APP, style="italic dim cyan"),
            title_align="right",
            subtitle=Text.from_markup(
                "[ " + arrow.now().format("HH:mm:ss") + " ]", style="not bold dim cyan"
            ),
            subtitle_align="left",
        )
    )


def initialize_partial_app(app: Flask, port: int):
    global _COOKIELIST_APP

    app.run = partial(
        app.run,
        extra_files=REQUIRE_RELOAD_FILES,
        port=port,
        reloader_type="_cookielist_werkzeug_reloader",
        host=env.string("APP_HOST"),
        ssl_context=(
            "adhoc" if env.string("APP_PROTOCOL") == "https" and DEBUG else None
        ),
    )

    _COOKIELIST_APP += ":{port}".format(port=port)

    if env.bool("COOKIELIST_DEBUG"):
        app.logger.disabled = True
        logging.getLogger("werkzeug").disabled = True
        warnings.filterwarnings(
            "ignore",
            message="Could not insert debug toolbar. </body> tag not found in response.",
        )
        flask.cli.show_server_banner = lambda *_, **__: None
        werkzeug._reloader.reloader_loops["_cookielist_werkzeug_reloader"] = (
            _ReloaderLoop
        )

        if env.bool("WERKZEUG_RUN_MAIN"):
            _log("[bold green]APP RELOADED[/]")
        else:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                try:
                    s.connect(("10.253.155.219", 58162))
                    address = s.getsockname()[0]
                except OSError:
                    address = "127.0.0.1"
            _log(
                "[bold italic yellow]APP STARTED AT[/]\n"
                + "\n".join(
                    [
                        f"[ [cyan]{env.string('APP_PROTOCOL')}://{addr}:{port}[/] ]"
                        for addr in ["127.0.0.1", "localhost", address]
                    ]
                )
            )
            if app.debug:
                _log("[bold red]RESTARTING WITH DEBUGGER[/]")

    return app


def _get_cookielist_core() -> Flask:
    return __import__(
        "cookielist.webapp", globals(), locals(), ["cookielist_core"], 0
    ).cookielist_core


def _get_cookielist_badge() -> Flask:
    return __import__(
        "cookielist.badgeapp", globals(), locals(), ["cookielist_badge"], 0
    ).cookielist_badge


def _get_cookielist_stub() -> Flask:
    return __import__(
        "cookielist.stubapp", globals(), locals(), ["cookielist_stub"], 0
    ).cookielist_stub


_cookielist_app_mapping: dict[str, Callable[[], Flask]] = {
    "cookielist-core-app": _get_cookielist_core,
    "cookielist-badge-app": _get_cookielist_badge,
    "cookielist-stub-app": _get_cookielist_stub,
    "cookielist-core-or-stub-app": (
        _get_cookielist_stub
        if not STATE_FOLDER.joinpath("cookielist.db").exists() and not DEBUG
        else _get_cookielist_core
    ),
}

_cookielist_app_theme_mapping = {
    "cookielist-core-app": "dim green bold",
    "cookielist-badge-app": "dim magenta bold",
    "cookielist-stub-app": "dim yellow bold",
    "cookielist-core-or-stub-app": (
        "dim yellow bold"
        if not STATE_FOLDER.joinpath("cookielist.db").exists() and not DEBUG
        else "dim green bold"
    ),
}


def get_app(_app: str):
    global _COOKIELIST_APP, _COOKIELIST_APP_THEME
    _COOKIELIST_APP = _app
    _COOKIELIST_APP_THEME = _cookielist_app_theme_mapping.get(_app, "bold dim white")
    if not env.bool("WERKZEUG_RUN_MAIN") and env.bool("COOKIELIST_DEBUG"):
        _log("[bold italic blue]STARTING COOKIELIST APP[/]")
    app = _cookielist_app_mapping[_app]()
    port = env.int("APP_PORT")
    if _app == "cookielist-badge-app":
        port = env.int("BADGE_APP_PORT")
    if DEBUG:
        return initialize_partial_app(app, port)
    return app


@click.group()
@click.pass_context
def cli(ctx):
    pass


@cli.command()
@click.option("-a", "--app", default="cookielist-core-or-stub-app", type=str)
def run(app: str):
    cookie_app = get_app(app)
    while True:
        try:
            cookie_app.run()
        except:
            time.sleep(1)
            cookie_app.run()


@cli.command()
@click.option("--db-last-page", type=int, default=None)
def synchronize(db_last_page: int):
    if db_last_page is None:
        env.environ["DATABASE_LAST_PAGE_ESTIMATE"] = str(db_last_page)
    from cookielist.synchronize import CookieListSynchronizer

    CookieListSynchronizer().synchronize()


@cli.command()
def github_action_set_estimate():
    from cookielist.synchronize import set_last_database_page_github_output

    set_last_database_page_github_output()


@cli.command()
@click.option("-g", "--group", type=int, required=True)
@click.option("-t", "--total", type=int, required=True)
def prefetch(group: int, total: int):
    from cookielist.synchronize import prefetch

    prefetch(group, total)


if __name__ == "__main__":
    cli()
