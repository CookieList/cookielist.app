import os

import rich
from rich import pretty, traceback

from cookielist.environment import env

env.path("COOKIELIST_STATE_FOLDER").mkdir(parents=True, exist_ok=True)

if os.getenv("COOKIELIST_DEBUG").lower() == "true":
    rich.reconfigure(
        force_terminal=os.getenv("GITHUB_ACTIONS") == "true"
        if os.getenv("GITHUB_ACTIONS")
        else None
    )
    pretty.install()
    traceback.install(
        console=rich.get_console(),
        width=120,
        show_locals=True,
    )
