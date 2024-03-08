from pathlib import Path

from cookielist.badge.template import BadgeTemplates

TEMPLATES = list(
    map(
        lambda _: _.name.replace("-", " ").title(),
        [
            path
            for path in Path(__file__).parent.joinpath("templates").iterdir()
            if path.joinpath("__badge__.svg").is_file()
            and path.joinpath("__badge__.svg").exists()
        ],
    )
)
