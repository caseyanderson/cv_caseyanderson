from pathlib import Path

from jinja2 import (
    Environment,
    FileSystemLoader,
    StrictUndefined,
    select_autoescape,
)

_TEMPLATE_DIRECTORY = Path(__file__).parent / "templates"


def create_environment() -> Environment:
    return Environment(
        loader=FileSystemLoader(_TEMPLATE_DIRECTORY),
        autoescape=select_autoescape(
            enabled_extensions=(
                "html",
                "htm",
                "xml",
                "jinja",
            ),
            default_for_string=True,
            default=True,
        ),
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render_cv(
    cv: dict[str, object],
) -> str:
    sections = cv.get("sections")

    if not isinstance(sections, list):
        raise TypeError("CV sections must be a list")

    template = create_environment().get_template("index.html.jinja")

    return template.render(sections=sections)
