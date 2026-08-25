import pytest

from teamdynamix._response import as_dict, as_list_of_dicts, first_dict_or_none


@pytest.mark.parametrize("value", [None, [], {}, "unexpected", 0, False])
def test_as_list_of_dicts_normalizes_empty_and_non_container_values(value) -> None:
    assert as_list_of_dicts(value) == []


def test_as_list_of_dicts_wraps_dict_and_filters_mixed_lists() -> None:
    payload = {"ID": 1}

    assert as_list_of_dicts(payload) == [payload]
    assert as_list_of_dicts([payload, "ignored", {"ID": 2}, None]) == [
        payload,
        {"ID": 2},
    ]


@pytest.mark.parametrize("value", [None, {}, [], "unexpected", 0, False])
def test_as_dict_returns_none_for_empty_or_non_dict_values(value) -> None:
    assert as_dict(value) is None


def test_as_dict_preserves_non_empty_dict() -> None:
    payload = {"ID": 1}

    assert as_dict(payload) is payload


def test_first_dict_or_none_preserves_legacy_first_entry_semantics() -> None:
    empty: dict[str, object] = {}
    first = {"ID": 1}

    assert first_dict_or_none(empty) is empty
    assert first_dict_or_none(first) is first
    assert first_dict_or_none([first, {"ID": 2}]) is first
    assert first_dict_or_none(["ignored", first]) is None
    assert first_dict_or_none([]) is None
    assert first_dict_or_none(None) is None
