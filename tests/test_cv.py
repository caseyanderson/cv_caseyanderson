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

    def test_education_concentration_and_exact_date(self):
        render_education_entry = (
            create_environment()
            .get_template("macros.html.jinja")
            .module.render_education_entry
        )
        education = next(
            section
            for section in self.cv["sections"]
            if section["id"] == "education"
        )
        calarts = next(
            entry
            for entry in education["entries"]
            if entry["institution"] == "California Institute of the Arts"
        )
        fallback = copy.deepcopy(calarts)
        del fallback["concentration"]

        self.assertEqual(calarts["major"], ["Music Composition"])
        self.assertEqual(
            calarts["concentration"],
            "Experimental Sound Practices",
        )
        self.assertEqual(
            calarts["time"]["value"],
            {"year": 2009, "month": 5, "day": 15},
        )

        for entry, expected_label in (
            (calarts, "MFA in Experimental Sound Practices"),
            (fallback, "MFA in Music Composition"),
        ):
            with self.subTest(label=expected_label):
                element = ElementTree.fromstring(
                    f"<div>{render_education_entry(entry)}</div>"
                )
                time_element = element.find("time")

                self.assertEqual(
                    element.find("span").text,
                    expected_label,
                )
                self.assertEqual(
                    time_element.attrib["datetime"],
                    "2009",
                )
                self.assertEqual(
                    "".join(time_element.itertext()).strip(),
                    "2009",
                )


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


class TestCVValidationBoundaries(unittest.TestCase):
    def setUp(self):
        self.cv = load_cv(CV_PATH)

    def test_unknown_section_is_rejected(self):
        candidate = copy.deepcopy(self.cv)
        candidate["sections"].append({
            "id": "unknown-section",
            "title": "Unknown Section",
            "entries": [],
        })

        with self.assertRaisesRegex(ValueError, "Unknown CV section"):
            _validate_cv(candidate)

    def test_missing_section_id_is_rejected(self):
        candidate = copy.deepcopy(self.cv)
        del candidate["sections"][0]["id"]

        with self.assertRaisesRegex(ValueError, "Unknown CV section"):
            _validate_cv(candidate)

    def test_non_string_section_ids_are_rejected(self):
        for section_id in (None, 123, False, [], {}):
            with self.subTest(section_id=section_id):
                candidate = copy.deepcopy(self.cv)
                candidate["sections"][0]["id"] = section_id

                with self.assertRaisesRegex(ValueError, "Unknown CV section"):
                    _validate_cv(candidate)

    def test_missing_section_titles_are_rejected(self):
        for index, section in enumerate(self.cv["sections"]):
            with self.subTest(section=section["id"]):
                candidate = copy.deepcopy(self.cv)
                del candidate["sections"][index]["title"]

                with self.assertRaisesRegex(ValueError, "title"):
                    _validate_cv(candidate)

    def test_non_string_section_titles_are_rejected(self):
        for index, section in enumerate(self.cv["sections"]):
            for title in (None, 123, False, [], {}):
                with self.subTest(section=section["id"], title=title):
                    candidate = copy.deepcopy(self.cv)
                    candidate["sections"][index]["title"] = title

                    with self.assertRaisesRegex(ValueError, "title"):
                        _validate_cv(candidate)

    def test_custom_string_section_titles_are_allowed(self):
        candidate = copy.deepcopy(self.cv)
        for section in candidate["sections"]:
            section["title"] = f"Selected {section['title']}"

        original = copy.deepcopy(candidate)
        _validate_cv(candidate)

        self.assertEqual(candidate, original)


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
