import copy
import json
import unittest
from pathlib import Path

from cv_caseyanderson.content import _validate_section_schema, load_cv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIRECTORY = PROJECT_ROOT / "src/cv_caseyanderson/schemas"

MULTIPLE_DATE_SECTIONS = {
    "teaching.schema.json": "teaching",
    "guest-lectures-artist-talks.schema.json": "guest-lectures-artist-talks",
    "design-production.schema.json": "selected-projects-production",
}

SINGLE_DATE_SECTIONS = {
    "education.schema.json": ("education", "time"),
    "conferences.schema.json": ("conferences", "time"),
    "publications.schema.json": ("publications", "time"),
    "selected-discography.schema.json": ("selected-discography", "time"),
    "guest-lectures-artist-talks.schema.json": (
        "guest-lectures-artist-talks",
        "date",
    ),
}


def get_single_date_definition(schema, location):
    if location == "time":
        return schema["properties"]["entries"]["items"]["properties"]["time"]

    return schema["$defs"]["date"]


class TestSharedDates(unittest.TestCase):
    def setUp(self):
        cv = load_cv(PROJECT_ROOT / "data/cv.json")
        self.sections = {section["id"]: section for section in cv["sections"]}

    def test_sections_reference_shared_dates(self):
        for filename in MULTIPLE_DATE_SECTIONS:
            with self.subTest(schema=filename):
                schema = json.loads(
                    (SCHEMA_DIRECTORY / filename).read_text(encoding="utf-8")
                )

                self.assertEqual(
                    schema["$defs"]["dates"],
                    {"$ref": "urn:cv-caseyanderson:schema:dates"},
                )

    def assert_time_examples(self, examples, valid):
        for filename, section_id in MULTIPLE_DATE_SECTIONS.items():
            for label, time in examples.items():
                with self.subTest(schema=filename, example=label):
                    candidate = copy.deepcopy(self.sections[section_id])
                    candidate["entries"][0]["time"] = copy.deepcopy(time)

                    if valid:
                        _validate_section_schema(
                            candidate, filename, candidate["title"]
                        )
                    else:
                        with self.assertRaises(ValueError):
                            _validate_section_schema(
                                candidate, filename, candidate["title"]
                            )

    def test_valid_multiple_dates_are_accepted(self):
        examples = {
            "one date": {
                "kind": "dates",
                "values": [{"year": 2025}],
            },
            "two dates": {
                "kind": "dates",
                "values": [
                    {"year": 2019, "month": 5, "day": 17},
                    {"year": 2019, "month": 5, "day": 18},
                ],
            },
            "null optional fields": {
                "kind": "dates",
                "values": [
                    {"year": 2025, "month": None, "season": None},
                ],
            },
        }

        self.assert_time_examples(examples, valid=True)

    def test_invalid_multiple_dates_are_rejected(self):
        examples = {
            "empty dates": {
                "kind": "dates",
                "values": [],
            },
            "missing values": {
                "kind": "dates",
            },
            "wrong values type": {
                "kind": "dates",
                "values": "2025",
            },
            "missing year": {
                "kind": "dates",
                "values": [{"month": 5}],
            },
            "invalid month": {
                "kind": "dates",
                "values": [{"year": 2025, "month": 13}],
            },
            "day without month": {
                "kind": "dates",
                "values": [{"year": 2025, "day": 2}],
            },
            "extra time field": {
                "kind": "dates",
                "values": [{"year": 2025}],
                "unexpected": True,
            },
        }

        self.assert_time_examples(examples, valid=False)


class TestSharedSingleDates(unittest.TestCase):
    def setUp(self):
        cv = load_cv(PROJECT_ROOT / "data/cv.json")
        self.sections = {section["id"]: section for section in cv["sections"]}

    def test_sections_reference_shared_single_date(self):
        for filename, (_, location) in SINGLE_DATE_SECTIONS.items():
            with self.subTest(schema=filename):
                schema = json.loads(
                    (SCHEMA_DIRECTORY / filename).read_text(encoding="utf-8")
                )

                self.assertEqual(
                    get_single_date_definition(schema, location),
                    {"$ref": "urn:cv-caseyanderson:schema:single-date"},
                )

    def assert_time_examples(self, examples, valid):
        for filename, (section_id, _) in SINGLE_DATE_SECTIONS.items():
            for label, time in examples.items():
                with self.subTest(schema=filename, example=label):
                    candidate = copy.deepcopy(self.sections[section_id])
                    candidate["entries"][0]["time"] = copy.deepcopy(time)

                    if valid:
                        _validate_section_schema(
                            candidate, filename, candidate["title"]
                        )
                    else:
                        with self.assertRaises(ValueError):
                            _validate_section_schema(
                                candidate, filename, candidate["title"]
                            )

    def test_valid_single_dates_are_accepted(self):
        examples = {
            "one date": {
                "kind": "date",
                "value": {"year": 2025},
            },
            "full date": {
                "kind": "date",
                "value": {"year": 2019, "month": 5, "day": 17},
            },
            "null optional fields": {
                "kind": "date",
                "value": {"year": 2025, "month": None, "season": None},
            },
            "extra wrapper field": {
                "kind": "date",
                "value": {"year": 2025},
                "unexpected": True,
            },
        }

        self.assert_time_examples(examples, valid=True)

    def test_invalid_single_dates_are_rejected(self):
        examples = {
            "missing kind": {
                "value": {"year": 2025},
            },
            "missing value": {
                "kind": "date",
            },
            "wrong kind": {
                "kind": "dates",
                "value": {"year": 2025},
            },
            "wrong value type": {
                "kind": "date",
                "value": "2025",
            },
            "missing year": {
                "kind": "date",
                "value": {"month": 5},
            },
            "invalid month": {
                "kind": "date",
                "value": {"year": 2025, "month": 13},
            },
            "day without month": {
                "kind": "date",
                "value": {"year": 2025, "day": 2},
            },
        }

        self.assert_time_examples(examples, valid=False)


if __name__ == "__main__":
    unittest.main()
