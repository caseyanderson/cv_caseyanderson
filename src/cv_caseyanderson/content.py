import json
from pathlib import Path
from typing import cast


def load_cv(path: Path) -> dict[str, object]:

    raw_data = cast(
        object,
        json.loads(path.read_text(encoding="utf-8")),
    )

    if not isinstance(raw_data, dict):
        raise TypeError("CV data must be a JSON object")

    return cast(dict[str, object], raw_data)
