import copy
import json
import unittest
from pathlib import Path

from cv_caseyanderson.content import _validate_section_schema, load_cv

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_DIRECTORY = PROJECT_ROOT / "src/cv_caseyanderson/schemas"

SCHEMA_SECTIONS = {
    "teaching.schema.json": "teaching",
    "guest-lectures-artist-talks.schema.json": "guest-lectures-artist-talks",
    "design-production.schema.json": "selected-projects-production",
}


class TestSharedDates(unittest.TestCase):
    def setUp(self):
        cv = load_cv(PROJECT_ROOT / "data/cv.json")
        self.sections = {
            section["id"]: section
            for section in cv["sections"]
        }

    def test_sections_reference_shared_dates(self):
        for filename in SCHEMA_SECTIONS:
            with self.subTest(schema=filename):
                schema = json.loads(
                    (SCHEMA_DIRECTORY / filename).read_text(
                        encoding="utf-8"
                    )
                )

                self.assertEqual(
                    schema["$defs"]["dates"],
                    {"$ref": "urn:cv-caseyanderson:schema:dates"},
                )

    def assert_time_examples(self, examples, valid):
        for filename, section_id in SCHEMA_SECTIONS.items():
            for label, time in examples.items():
                with self.subTest(schema=filename, example=label):
                    candidate = copy.deepcopy(
                        self.sections[section_id]
                    )
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


if __name__ == "__main__":
    unittest.main()