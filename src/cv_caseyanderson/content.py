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

_PROFESSIONAL_REQUIRED_KEYS = {
    "organization",
    "role",
    "location",
    "time",
}

_TEACHING_REQUIRED_KEYS = {
    "institution",
    "role",
    "location",
    "time",
}

_DATE_COMPONENT_KEYS = {
    "year",
    "month",
    "season",
}

_VALID_SEASONS = {
    "spring",
    "summer",
    "fall",
    "winter",
}

_INTERVAL_KEYS = {
    "kind",
    "start",
    "end",
}

_DATES_KEYS = {
    "kind",
    "values",
}


def _is_nonempty_string_list(
    value: object,
) -> bool:
    if not isinstance(value, list):
        return False

    string_values = cast(
        list[object],
        value,
    )

    return len(string_values) > 0 and all(
        isinstance(item, str) for item in string_values
    )


def _has_valid_education_text_fields(
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


def _has_valid_professional_text_fields(
    entry: dict[str, object],
) -> bool:
    return all(
        isinstance(entry.get(key), str)
        for key in (
            "organization",
            "location",
        )
    )


def _has_valid_teaching_text_fields(
    entry: dict[str, object],
) -> bool:
    return all(
        isinstance(entry.get(key), str)
        for key in (
            "institution",
            "location",
        )
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
    season = component.get("season")

    if month is not None and season is not None:
        return False

    if month is not None:
        if type(month) is not int:
            return False

        if not 1 <= month <= 12:
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


def _is_valid_interval(
    value: object,
) -> bool:
    if not isinstance(value, dict):
        return False

    interval = cast(
        dict[str, object],
        value,
    )

    if set(interval.keys()) != _INTERVAL_KEYS:
        return False

    if interval.get("kind") != "interval":
        return False

    if not _is_valid_date_component(interval.get("start")):
        return False

    end = interval.get("end")

    return end is None or _is_valid_date_component(end)


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


def _is_valid_teaching_time(
    value: object,
) -> bool:
    return _is_valid_interval(value) or _is_valid_dates(value)


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
        and _has_valid_education_text_fields(entry)
        and _is_nonempty_string_list(entry.get("major"))
        and _has_valid_time(entry.get("time"))
    )


def _is_valid_professional_entry(
    value: object,
) -> bool:
    if not isinstance(value, dict):
        return False

    entry = cast(
        dict[str, object],
        value,
    )

    return (
        set(entry.keys()) == _PROFESSIONAL_REQUIRED_KEYS
        and _has_valid_professional_text_fields(entry)
        and _is_nonempty_string_list(entry.get("role"))
        and _is_valid_interval(entry.get("time"))
    )


def _is_valid_teaching_entry(
    value: object,
) -> bool:
    if not isinstance(value, dict):
        return False

    entry = cast(
        dict[str, object],
        value,
    )

    return (
        set(entry.keys()) == _TEACHING_REQUIRED_KEYS
        and _has_valid_teaching_text_fields(entry)
        and _is_nonempty_string_list(entry.get("role"))
        and _is_valid_teaching_time(entry.get("time"))
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


def _validate_professional_section(
    section: dict[str, object],
) -> None:
    entries_value = section.get("entries")

    if not isinstance(entries_value, list):
        raise TypeError("Professional Experience entries must be a list")

    entries = cast(
        list[object],
        entries_value,
    )

    if not entries:
        raise ValueError("Professional Experience entries must not be empty")

    for index, entry in enumerate(entries):
        if not _is_valid_professional_entry(entry):
            raise ValueError("Invalid Professional Experience entry " + str(index))


def _validate_teaching_section(
    section: dict[str, object],
) -> None:
    entries_value = section.get("entries")

    if not isinstance(entries_value, list):
        raise TypeError("Teaching entries must be a list")

    entries = cast(
        list[object],
        entries_value,
    )

    if not entries:
        raise ValueError("Teaching entries must not be empty")

    for index, entry in enumerate(entries):
        if not _is_valid_teaching_entry(entry):
            raise ValueError("Invalid Teaching entry " + str(index))


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

    if education_section is None:
        raise ValueError("CV must contain an Education section")

    if professional_section is None:
        raise ValueError("CV must contain a Professional Experience section")

    if teaching_section is None:
        raise ValueError("CV must contain a Teaching section")

    _validate_education_section(education_section)

    _validate_professional_section(professional_section)

    _validate_teaching_section(teaching_section)


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
