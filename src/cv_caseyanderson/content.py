import json
from pathlib import Path
from typing import cast

_EDUCATION_REQUIRED_KEYS = {
    "degree",
    "major",
    "institution",
    "location",
    "time",
}


def _has_valid_majors(majors: object) -> bool:
    if not isinstance(majors, list):
        return False

    major_values = cast(
        list[object],
        majors,
    )

    return len(major_values) > 0 and all(
        isinstance(major, str) for major in major_values
    )


def _has_valid_text_fields(
    entry: dict[str, object],
) -> bool:
    return all(
        isinstance(entry.get(key), str)
        for key in (
            "degree",
            "institution",
            "location",
        )
    )


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

    if not isinstance(date_value, dict):
        return False

    date_data = cast(
        dict[str, object],
        date_value,
    )

    return type(date_data.get("year")) is int


def _is_valid_education_entry(
    entry_value: object,
) -> bool:
    if not isinstance(entry_value, dict):
        return False

    entry = cast(
        dict[str, object],
        entry_value,
    )

    return (
        _EDUCATION_REQUIRED_KEYS.issubset(entry.keys())
        and _has_valid_text_fields(entry)
        and _has_valid_majors(entry.get("major"))
        and _has_valid_time(entry.get("time"))
    )


def _validate_education_section(
    section: dict[str, object],
) -> None:
    entries_value = section.get("entries")

    if not isinstance(entries_value, list):
        raise TypeError("Education entries must be a list")

    entries = cast(
        list[object],
        entries_value,
    )

    if not entries:
        raise ValueError("Education entries must not be empty")

    for index, entry in enumerate(entries):
        if not _is_valid_education_entry(entry):
            raise ValueError("Invalid Education entry " + str(index))


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

    for section_value in sections:
        if not isinstance(section_value, dict):
            raise TypeError("Each CV section must be an object")

        section = cast(
            dict[str, object],
            section_value,
        )

        if section.get("id") != "education":
            continue

        if education_section is not None:
            raise ValueError("CV must contain only one Education section")

        education_section = section

    if education_section is None:
        raise ValueError("CV must contain an Education section")

    _validate_education_section(education_section)


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
