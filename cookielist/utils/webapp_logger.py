import string
from time import time

import jsonurl_py as jsonurl
import orjson
from flask import Response, g, request
import arrow
from rich.console import Console
from rich.highlighter import Highlighter
from yurl import URL

from cookielist.environment import env


class UriHighlighter(Highlighter):
    def highlight(self, text):
        components = URL(text.plain)
        markup = ""

        if components.scheme:
            if components.scheme == "https":
                markup += f"[green dim]{components.scheme}[/green dim]"
            elif components.scheme == "http":
                markup += f"[red dim]{components.scheme}[/red dim]"
            else:
                markup += f"[yellow dim]{components.scheme}[/yellow dim]"
            markup += "[white dim]://[/white dim]"
        if components.userinfo:
            markup += (
                f"[italic blue]{components.userinfo}[/italic blue][dim]@[/dim]".replace(
                    ":", "[white dim]:[/white dim]"
                )
            )
        if components.host:
            markup += f"[bold blue]{components.host}[/bold blue]"
        if components.port:
            markup += (
                f"[white dim]:[/white dim][italic blue]{components.port}[/italic blue]"
            )
        if components.path:
            path: str = components.path
            if not path.startswith("/"):
                path = "/" + path
            paths = list(filter(lambda _: _, path.split("/")))
            for number, _path in enumerate(paths, start=1):
                if number != len(paths):
                    markup += f"[white dim]/[/white dim][green]{_path}[/green]"
                else:
                    markup += (
                        f"[white dim]/[/white dim][green bold]{_path}[/green bold]"
                    )
        if components.query:
            markup += f"[white dim]?[/white dim]"
            for number, query in enumerate(components.query.split("&"), start=1):
                parts = query.split("=", 1)
                if len(parts) <= 1:
                    key, value = "", parts[-1]
                else:
                    key, value = tuple(parts)
                markup += f"[yellow bold]{key}[/yellow bold][white dim]{'=' if key else ''}[/white dim][yellow italic]{value}[/yellow italic]"
                if number != len(components.query.split("&")):
                    markup += "[white dim]&[/white dim]"
        if components.fragment:
            markup += f"[white dim]#[/white dim][green dim italic]{components.fragment}[/green dim italic]"

        highlighted = text.from_markup(markup)
        text._text = highlighted._text
        text._spans = highlighted._spans


console = Console()
_uri_highlighter = UriHighlighter()
jsonurl.check_can_mark_safe = lambda *_, **__: None
jsonurl_options = jsonurl.DumpOpts(
    distinguish_empty_list_dict=True, safe=string.printable, implied_dict=True
)

METHODS = dict(
    GET="bold magenta",
    POST="bold yellow",
    PUT="bold blue",
    DELETE="bold red",
    HEAD="bold cyan",
)

CODES = {
    200: "italic blue",
    304: "dim blue italic",
    404: "magenta italic bold",
    302: "dim white",
    500: "red italic",
}

if env.bool("COOKIELIST_DEBUG"):
    __log_file = env.path("STATISTICS_LOG_FILE").open("a", encoding="utf-8")
    __flush = lambda string, __file=__log_file: print(
        arrow.now().format("YYYY-MM-DD HH:mm:ss ") + string.replace("\n", "<?:br!>"), flush=True, file=__file
    )
else:
    __flush = lambda string: print(string.replace("\n", "<?:br!>"))


def make_request_log(response: Response | None = None):
    if response is not None:
        status_code = response.status_code
        _eof = "\n"
    else:
        status_code = "●●●"
        _eof = "\r"

    method_style = METHODS.get(request.method, "bold")
    code_style = CODES.get(status_code, "red bold")
    path = request.url

    if console.width < len(path) + 28:
        path = path[: console.width - 28] + "..."

    console.print(
        f"[bold dim white]{{•}}[/bold dim white] [{method_style}]{request.method: >7}[/{method_style}]  [dim]•[/dim]  [{code_style}]{status_code: >3}[/{code_style}][dim]  •  [/dim]",
        _uri_highlighter(path),
        " " * (console.width - len(path)),
        end=_eof,
    )


def make_stats_log(response: Response):
    statistics = orjson.dumps(
        [
            request.headers.get(
                "X-Real-IP", default=request.remote_addr
            ),  # Request IP Address
            request.method,  # Request Method
            request.environ.get("SERVER_PROTOCOL"),  # Request Server Protocol
            response.status_code,  # Response Status-Code
            request.url_rule.rule if request.url_rule is not None else request.path,  # Request Endpoint
            request.view_args,  # Endpoint Arguments
            request.args,  # Url Arguments
            round(time() - g.request_start_time, 3),  # Time Taken To Respond
            g.session_id,  # Unique Session Identifier
            response.content_length,  # Response Data Size In Bytes
            request.origin,  # Request Referrer
            request.user_agent.string,  # Request User Agent
        ]
    ).decode()
    __flush("{#} " + statistics)


def make_session_id_log(session_id: str):
    __flush(
        "{$} " + orjson.dumps([g.session_id, session_id]).decode()
    )  # [previous, current]


def make_traceback_log(traceback: str, trace_id: str):
    __flush(
        "{!} " + orjson.dumps([traceback, trace_id]).decode()
    )  # [traceback, trace_id]


def make_badge_log(response: Response):
    __flush(
        "{|} "
        + orjson.dumps(
            [
                request.headers.get("X-Real-IP", default=request.remote_addr), # Request IP Address
                request.method, # Request Method
                response.status_code, # # Response Status-Code
                request.url_rule.rule if request.url_rule is not None else request.path, # Request Endpoint
                request.view_args, # Request Arguments
                round(time() - g.request_start_time, 3),  # Time Taken To Respond
                response.content_length, # Response Data Size In Bytes
                request.origin, #  Request Referrer
            ]
        ).decode()
    )
