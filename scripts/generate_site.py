from pathlib import Path

from cv_caseyanderson.content import load_cv
from cv_caseyanderson.render import render_cv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "cv.json"
OUTPUT_PATH = PROJECT_ROOT / "index.html"


def main() -> None:
    cv = load_cv(DATA_PATH)
    html = render_cv(cv)

    _ = OUTPUT_PATH.write_text(
        html,
        encoding="utf-8",
        newline="\n",
    )

    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
