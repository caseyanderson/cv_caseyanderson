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


_GUEST_LECTURE_REQUIRED_KEYS = {
    "institution",
    "title",
    "context",
    "location",
    "time",
}

_GUEST_LECTURE_CONTEXT_REQUIRED_KEYS = {
    "name",
    "host",
}

_CONFERENCE_REQUIRED_KEYS = {
    "title",
    "conference",
    "collaborators",
    "location",
    "time",
}

_DATE_COMPONENT_KEYS = {
    "year",
    "month",
    "day",
    "season",
}

_VALID_SEASONS = {
    "spring",
    "summer",
    "fall",
    "winter",
}


_DATES_KEYS = {
    "kind",
    "values",
}


def _is_string_list(
    value: object,
) -> bool:
    if not isinstance(value, list):
        return False

    string_values = cast(
        list[object],
        value,
    )

    return all(isinstance(item, str) for item in string_values)


def _has_valid_guest_lecture_text_fields(
    entry: dict[str, object],
) -> bool:
    return all(
        isinstance(entry.get(key), str)
        for key in (
            "institution",
            "title",
            "location",
        )
    )


def _is_valid_guest_lecture_context(
    value: object,
) -> bool:
    if not isinstance(value, dict):
        return False

    context = cast(
        dict[str, object],
        value,
    )

    return set(context.keys()) == _GUEST_LECTURE_CONTEXT_REQUIRED_KEYS and all(
        isinstance(context.get(key), str)
        for key in _GUEST_LECTURE_CONTEXT_REQUIRED_KEYS
    )


def _is_valid_date_component(
    value: object,
) -> bool:
    if not isinstance(value, dict):
        return False

    component = cast(
        dict[str, object],
        value,
    )

    if not component.keys() <= _DATE_COMPONENT_KEYS:
        return False

    if type(component.get("year")) is not int:
        return False

    month = component.get("month")
    day = component.get("day")
    season = component.get("season")

    if month is not None and season is not None:
        return False

    if month is not None:
        if type(month) is not int:
            return False

        if not 1 <= month <= 12:
            return False

    if day is not None:
        if month is None:
            return False

        if type(day) is not int:
            return False

        if not 1 <= day <= 31:
            return False

    if season is not None:
        if not isinstance(season, str):
            return False

        if season not in _VALID_SEASONS:
            return False

    return True


def _has_valid_time(time_value: object) -> bool:
    if not isinstance(time_value, dict):
        return False

    time_data = cast(
        dict[str, object],
        time_value,
    )

    if time_data.get("kind") != "date":
        return False

    date_value = time_data.get("value")

    return _is_valid_date_component(date_value)


def _is_valid_dates(
    value: object,
) -> bool:
    if not isinstance(value, dict):
        return False

    dates_data = cast(
        dict[str, object],
        value,
    )

    if set(dates_data.keys()) != _DATES_KEYS:
        return False

    if dates_data.get("kind") != "dates":
        return False

    values_value = dates_data.get("values")

    if not isinstance(values_value, list):
        return False

    date_values = cast(
        list[object],
        values_value,
    )

    return len(date_values) > 0 and all(
        _is_valid_date_component(date_value) for date_value in date_values
    )


def _is_valid_guest_lecture_time(
    value: object,
) -> bool:
    return _has_valid_time(value) or _is_valid_dates(value)


def _is_valid_guest_lecture_entry(
    value: object,
) -> bool:
    if not isinstance(value, dict):
        return False

    entry = cast(
        dict[str, object],
        value,
    )

    return (
        set(entry.keys()) == _GUEST_LECTURE_REQUIRED_KEYS
        and _has_valid_guest_lecture_text_fields(entry)
        and _is_valid_guest_lecture_context(entry.get("context"))
        and _is_valid_guest_lecture_time(entry.get("time"))
    )


def _is_valid_conference_entry(
    value: object,
) -> bool:
    if not isinstance(value, dict):
        return False

    entry = cast(
        dict[str, object],
        value,
    )

    return (
        set(entry.keys()) == _CONFERENCE_REQUIRED_KEYS
        and all(
            isinstance(entry.get(key), str)
            for key in ("title", "conference", "location")
        )
        and _is_string_list(entry.get("collaborators"))
        and _has_valid_time(entry.get("time"))
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


def _validate_guest_lecture_section(
    section: dict[str, object],
) -> None:
    entries_value = section.get("entries")

    if not isinstance(entries_value, list):
        raise TypeError("Guest Lectures & Artist Talks entries must be a list")

    entries = cast(
        list[object],
        entries_value,
    )

    if not entries:
        raise ValueError("Guest Lectures & Artist Talks entries must not be empty")

    for index, entry in enumerate(entries):
        if not _is_valid_guest_lecture_entry(entry):
            raise ValueError(
                "Invalid Guest Lectures & Artist Talks entry " + str(index)
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


def _validate_conference_section(
    section: dict[str, object],
) -> None:
    entries_value = section.get("entries")

    if not isinstance(entries_value, list):
        raise TypeError("Conferences entries must be a list")

    entries = cast(
        list[object],
        entries_value,
    )

    if not entries:
        raise ValueError("Conferences entries must not be empty")

    for index, entry in enumerate(entries):
        if not _is_valid_conference_entry(entry):
            raise ValueError("Invalid Conferences entry " + str(index))


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

    _validate_education_section(education_section)

    _validate_professional_section(professional_section)

    _validate_teaching_section(teaching_section)

    _validate_guest_lecture_section(guest_lecture_section)

    _validate_awards_events_section(awards_events_section)

    _validate_conference_section(conference_section)


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
