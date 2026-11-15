import json
from pathlib import Path
from typing import cast

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.protocols import Validator
from referencing import Registry, Resource
from referencing.jsonschema import Schema

type JsonValue = (
    str | int | float | bool | None | list[JsonValue] | dict[str, JsonValue]
)


def _validate_education_section(section: dict[str, object]) -> None:
    _validate_section_schema(
        section,
        "education.schema.json",
        "Education",
    )


def _validate_professional_section(section: dict[str, object]) -> None:
    _validate_section_schema(
        section,
        "professional-experience.schema.json",
        "Professional Experience",
    )


def _validate_teaching_section(section: dict[str, object]) -> None:
    _validate_section_schema(
        section,
        "teaching.schema.json",
        "Teaching",
    )


def _validate_guest_lecture_section(section: dict[str, object]) -> None:
    _validate_section_schema(
        section,
        "guest-lectures-artist-talks.schema.json",
        "Guest Lectures & Artist Talks",
    )


def _validate_section_schema(
    section: dict[str, object],
    schema_filename: str,
    section_name: str,
) -> None:
    if not isinstance(section.get("entries"), list):
        raise TypeError(f"{section_name} entries must be a list")
    schema_directory = Path(__file__).parent / "schemas"
    schema = cast(
        dict[str, object],
        json.loads((schema_directory / schema_filename).read_text(encoding="utf-8")),
    )
    registry = Registry[Schema]()
    for shared_filename in ("date-component.schema.json", "interval.schema.json"):
        shared_schema = cast(
            dict[str, object],
            json.loads(
                (schema_directory / shared_filename).read_text(encoding="utf-8")
            ),
        )
        registry = registry.with_resource(
            cast(str, shared_schema["$id"]),
            Resource.from_contents(shared_schema),
        )
    validator = cast(
        Validator,
        Draft202012Validator(
            schema,
            format_checker=FormatChecker(),
            registry=registry,
        ),
    )
    instance = cast(dict[str, JsonValue], section)
    error = next(validator.iter_errors(instance), None)

    if error is not None:
        error_path = ".".join(str(component) for component in error.absolute_path)
        raise ValueError(
            f"Invalid {section_name} at {error_path or 'section'}: {error.message}"
        )


def _validate_awards_events_section(section: dict[str, object]) -> None:
    _validate_section_schema(
        section,
        "awards-events.schema.json",
        "Selected Awards, Distinctions, and Events",
    )


def _validate_conference_section(section: dict[str, object]) -> None:
    _validate_section_schema(
        section,
        "conferences.schema.json",
        "Conferences",
    )


def _validate_publications_section(section: dict[str, object]) -> None:
    _validate_section_schema(
        section,
        "publications.schema.json",
        "Publications",
    )


def _validate_discography_section(section: dict[str, object]) -> None:
    _validate_section_schema(
        section,
        "selected-discography.schema.json",
        "Selected Discography",
    )


def _validate_cv(
    cv: dict[str, object],
) -> None:
    sections_value = cv.get("sections")

    if not isinstance(sections_value, list):
        raise TypeError("CV sections must be a list")

    sections = cast(
        list[object],
        sections_value,
    )

    education_section: dict[str, object] | None = None
    professional_section: dict[str, object] | None = None
    teaching_section: dict[str, object] | None = None
    guest_lecture_section: dict[str, object] | None = None
    awards_events_section: dict[str, object] | None = None
    conference_section: dict[str, object] | None = None
    publications_section: dict[str, object] | None = None
    discography_section: dict[str, object] | None = None

    for section_value in sections:
        if not isinstance(section_value, dict):
            raise TypeError("Each CV section must be an object")

        section = cast(
            dict[str, object],
            section_value,
        )

        section_id = section.get("id")

        if section_id == "education":
            if education_section is not None:
                raise ValueError("CV must contain only one Education section")

            education_section = section

        elif section_id == "professional-experience":
            if professional_section is not None:
                raise ValueError(
                    "CV must contain only one Professional Experience section"
                )

            professional_section = section

        elif section_id == "teaching":
            if teaching_section is not None:
                raise ValueError("CV must contain only one Teaching section")

            teaching_section = section

        elif section_id == "guest-lectures-artist-talks":
            if guest_lecture_section is not None:
                raise ValueError(
                    "CV must contain only one Guest Lectures & Artist Talks section"
                )

            guest_lecture_section = section

        elif section_id == "selected-awards-distinctions-events":
            if awards_events_section is not None:
                raise ValueError(
                    "CV must contain only one Selected Awards, Distinctions, and Events section"
                )

            awards_events_section = section

        elif section_id == "conferences":
            if conference_section is not None:
                raise ValueError("CV must contain only one Conferences section")

            conference_section = section

        elif section_id == "publications":
            if publications_section is not None:
                raise ValueError("CV must contain only one Publications section")

            publications_section = section

        elif section_id == "selected-discography":
            if discography_section is not None:
                raise ValueError(
                    "CV must contain only one Selected Discography section"
                )

            discography_section = section

    if education_section is None:
        raise ValueError("CV must contain an Education section")

    if professional_section is None:
        raise ValueError("CV must contain a Professional Experience section")

    if teaching_section is None:
        raise ValueError("CV must contain a Teaching section")

    if guest_lecture_section is None:
        raise ValueError("CV must contain a Guest Lectures & Artist Talks section")

    if awards_events_section is None:
        raise ValueError(
            "CV must contain a Selected Awards, Distinctions, and Events section"
        )

    if conference_section is None:
        raise ValueError("CV must contain a Conferences section")

    if publications_section is None:
        raise ValueError("CV must contain a Publications section")

    if discography_section is None:
        raise ValueError("CV must contain a Selected Discography section")

    _validate_education_section(education_section)

    _validate_professional_section(professional_section)

    _validate_teaching_section(teaching_section)

    _validate_guest_lecture_section(guest_lecture_section)

    _validate_awards_events_section(awards_events_section)

    _validate_conference_section(conference_section)

    _validate_publications_section(publications_section)

    _validate_discography_section(discography_section)


def load_cv(path: Path) -> dict[str, object]:
    raw_data = cast(
        object,
        json.loads(path.read_text(encoding="utf-8")),
    )

    if not isinstance(raw_data, dict):
        raise TypeError("CV data must be a JSON object")

    cv = cast(
        dict[str, object],
        raw_data,
    )

    _validate_cv(cv)

    return cv
