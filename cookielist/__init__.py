import os
from pathlib import Path

import dotenv_vault
import rich
from rich import pretty, traceback


Path(os.getenv("COOKIELIST_STATE_FOLDER")).mkdir(parents=True, exist_ok=True)

if os.getenv("COOKIELIST_DEBUG").lower() == "true":
    rich.reconfigure(force_terminal=os.getenv("GITHUB_ACTIONS") == "true" if os.getenv("GITHUB_ACTIONS") else None)
    pretty.install()
    traceback.install(
        console=rich.get_console(),
        width=120,
        show_locals=True,
    )

