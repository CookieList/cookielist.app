import time
from pathlib import Path

from rich import print
from wcmatch import wcmatch
from wcmatch.pathlib import glob

import cookielist
from cookielist.environment import env

_DEBUG = env.bool("COOKIELIST_DEBUG")
_STATE_FOLDER = env.path("COOKIELIST_STATE_FOLDER")

if (not _DEBUG) and not (_STATE_FOLDER.joinpath('cookielist.db').exists()):
    print("[yellow]Warning:[/yellow] DEBUG mode disabled and state-folder is absent.")
    print("[cyan]Warning:[/cyan] stub-application would be used, until update.\n")

    from cookielist.stub_webapp import stub as app
else:
    from cookielist.webapp import cookielist as app
    


if __name__ == "__main__":
    debug_reload_extensions = ["jinja", "sass", "html", "js", "graphql"]

    run = lambda: app.run(
        host=env.string("APP_HOST"),
        port=env.int("APP_PORT"),
        extra_files=wcmatch.WcMatch(
            str(Path(cookielist.__file__).parent),
            f"*.@({'|'.join(debug_reload_extensions)})",
            flags=wcmatch.RECURSIVE | glob.EXTGLOB,
        ).match(),
    )

    while True:
        try:
            run()
        except Exception:
            run()
            time.sleep(1.5)
