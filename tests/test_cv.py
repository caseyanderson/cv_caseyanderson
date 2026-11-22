import copy
import unittest
from pathlib import Path
from xml.etree import ElementTree

from cv_caseyanderson.content import _validate_cv, load_cv
from cv_caseyanderson.render import create_environment, render_cv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CV_PATH = PROJECT_ROOT / "data" / "cv.json"
HTML_PATH = PROJECT_ROOT / "index.html"


def render_date_element(date, **options):
    render_date = (
        create_environment()
        .get_template("macros.html.jinja")
        .module.render_date_component
    )

    return ElementTree.fromstring(
        str(render_date(date, **options))
    )


class TestCVRendering(unittest.TestCase):
    def setUp(self):
        self.cv = load_cv(CV_PATH)

    def test_rendering_matches_saved_html(self):
        saved_html = HTML_PATH.read_text(encoding="utf-8")

        self.assertEqual(render_cv(self.cv), saved_html)

    def test_rendering_does_not_modify_data(self):
        original = copy.deepcopy(self.cv)

        render_cv(self.cv)

        self.assertEqual(self.cv, original)


class TestCVValidation(unittest.TestCase):
    def setUp(self):
        self.cv = load_cv(CV_PATH)

    def test_missing_sections_are_rejected(self):
        for section in self.cv["sections"]:
            with self.subTest(section=section["id"]):
                candidate = copy.deepcopy(self.cv)
                candidate["sections"] = [
                    item
                    for item in candidate["sections"]
                    if item["id"] != section["id"]
                ]

                with self.assertRaisesRegex(
                    ValueError, "must contain"
                ):
                    _validate_cv(candidate)

    def test_duplicate_sections_are_rejected(self):
        for section in self.cv["sections"]:
            with self.subTest(section=section["id"]):
                candidate = copy.deepcopy(self.cv)
                candidate["sections"].append(
                    copy.deepcopy(section)
                )

                with self.assertRaisesRegex(
                    ValueError, "only one"
                ):
                    _validate_cv(candidate)


class TestDateRendering(unittest.TestCase):
    def test_existing_date_formats(self):
        cases = [
            ({"year": 2025}, {}, "2025", "2025"),
            (
                {"year": 2025, "month": 9},
                {},
                "2025-09",
                "September 2025",
            ),
            (
                {"year": 2025, "month": 9, "day": 2},
                {},
                "2025-09-02",
                "September 2, 2025",
            ),
            (
                {"year": 2016, "season": "spring"},
                {},
                "2016",
                "Spring 2016",
            ),
            (
                {"year": 2025, "month": 9, "day": 2},
                {"show_day": False},
                "2025-09-02",
                "September 2025",
            ),
            (
                {"year": 2022, "month": 3, "day": 8},
                {"show_month": False},
                "2022-03-08",
                "2022",
            ),
        ]

        for date, options, datetime_value, visible_text in cases:
            with self.subTest(date=date, options=options):
                element = render_date_element(date, **options)

                self.assertEqual(element.tag, "time")
                self.assertEqual(
                    element.attrib["datetime"],
                    datetime_value,
                )
                self.assertEqual(
                    "".join(element.itertext()).strip(),
                    visible_text,
                )


class TestNullDateRendering(unittest.TestCase):
    def assert_rendered_date(
        self, date, datetime_value, visible_text
    ):
        element = render_date_element(date)

        self.assertEqual(
            element.attrib["datetime"],
            datetime_value,
        )
        self.assertEqual(
            "".join(element.itertext()).strip(),
            visible_text,
        )

    def test_null_month_behaves_like_missing_month(self):
        self.assert_rendered_date(
            {"year": 2025, "month": None},
            "2025",
            "2025",
        )

    def test_null_day_behaves_like_missing_day(self):
        self.assert_rendered_date(
            {"year": 2025, "month": 9, "day": None},
            "2025-09",
            "September 2025",
        )

    def test_null_season_behaves_like_missing_season(self):
        self.assert_rendered_date(
            {"year": 2025, "season": None},
            "2025",
            "2025",
        )


if __name__ == "__main__":
    unittest.main()