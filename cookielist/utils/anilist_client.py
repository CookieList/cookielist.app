import pathlib
import re
import time

import graphql
import orjson
import requests_cache
from rich import live, print, spinner

from cookielist.environment import env


class AnilistClient:
    ANILIST_API = "https://graphql.anilist.co/"
    ANILIST_AUTH = "https://anilist.co/api/v2/oauth/token"

    _session: requests_cache.CachedSession = None

    @property
    def session(self):
        if AnilistClient._session:
            return AnilistClient._session

        _session = requests_cache.CachedSession(
            str(
                env.path("COOKIELIST_STATE_FOLDER")
                .joinpath("httpcache.sqlite")
                .resolve()
            ),
            allowable_methods=("GET", "HEAD", "POST"),
            backend="sqlite",
        )

        AnilistClient._session = _session
        return _session

    def __init__(self, query: str | pathlib.Path, authorization: str = None) -> None:
        if authorization:
            self.session.headers.update(
                {
                    "Authorization": "Bearer " + authorization,
                }
            )

        if isinstance(query, pathlib.Path):
            query = query.read_text()

        self.gql_query = graphql.print_ast(graphql.parse(query))

    def query(
        self, operation: str, authorization: str = None, retry: int = 6, **variables
    ) -> dict:
        response = self.session.post(
            url=self.ANILIST_API,
            headers=(
                {"Authorization": "Bearer " + authorization} if authorization else {}
            ),
            data=dict(
                query=self.gql_query,
                variables=orjson.dumps(variables),
                operationName=operation,
            ),
        )

        try:
            content = response.json()
        except:
            message = response.text.strip()
            if message.startswith("<html>"):
                message = re.search("<title>(.*?)</title>", message, re.DOTALL)
                if message:
                    message = "*" + message.group(1).replace("\n", " ").strip()
                else:
                    message = response.text
            content = dict(
                data=None,
                errors=[dict(message=message, status=response.status_code)],
            )

        if (
            "Retry-After" in response.headers
            or "error" in content
            or "errors" in content
            or content.get("data") is None
        ) and retry >= 1:
            wait_time = int(response.headers.get("Retry-After", 8)) + 2
            try:
                if "errors" in content:
                    error = content.get(
                        "errors",
                        dict(message=response.text, status=response.status_code),
                    )
                    error_message = (
                        error[-1]["message"]
                        if isinstance(error, list)
                        else error["message"]
                    )
                    error_status = (
                        error[-1]["status"]
                        if isinstance(error, list)
                        else error["status"]
                    )
                elif "error" in content:
                    error = content.get(
                        "error",
                        dict(messages=response.text, status=response.status_code),
                    )
                    error_message = (
                        error["messages"][-1]
                        if isinstance(error["messages"], list)
                        else error["messages"]
                    )
                    error_status = error["status"]
                else:
                    error_message = "*" + response.text
                    error_status = response.status_code
            except Exception:
                error_message = "*" + response.text
                error_status = response.status_code

            print(
                f"[red]{{ANILIST API ERROR}}[/red] - ([blue]WAITING[/blue] [green]{wait_time:0>2} seconds[/green]) [red]{error_message}[/red] ([red]{error_status}[/red])"
            )

            time.sleep(wait_time)

            return self.query(
                operation=operation,
                authorization=authorization,
                retry=retry - 1,
                **variables,
            )

        return content["data"]

    def authorize(self, code: str) -> str | None:
        response = self.session.post(
            url=self.ANILIST_AUTH,
            headers={"Content-Type": "application/json", "Accept": "application/json"},
            json={
                "grant_type": "authorization_code",
                "client_id": env.string("AL_CLIENT_ID"),
                "client_secret": env.string("AL_CLIENT_SECRET"),
                "redirect_uri": env.string("AL_CLIENT_REDIRECT"),
                "code": code,
            },
        )
        return response.json().get("access_token", None)

    def estimate_end_page_of_query(
        self,
        operation: str,
        page_variable: str,
        page_jumps: int = 50,
        authorization: str = None,
        **variables,
    ) -> int:
        _has_next_page = True
        page = 0

        if env.bool("GITHUB_ACTIONS", False):
            print("[yellow]Acquiring Task Info[/yellow]")
            while _has_next_page:
                response = self.query(
                    operation,
                    authorization=authorization,
                    **variables | {page_variable: (page := page + page_jumps)},
                )
                _has_next_page = response["Page"]["pageInfo"]["hasNextPage"]
        else:
            with live.Live(
                spinner.Spinner("arc", text=" [yellow]Acquiring Task Info[/yellow]"),
                transient=True,
                refresh_per_second=10,
            ):
                while _has_next_page:
                    response = self.query(
                        operation,
                        authorization=authorization,
                        **variables | {page_variable: (page := page + page_jumps)},
                    )
                    _has_next_page = response["Page"]["pageInfo"]["hasNextPage"]

        return page + 1
