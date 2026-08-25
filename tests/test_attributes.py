from typing import Any
from unittest.mock import MagicMock

from teamdynamix.attributes import (
    Attribute,
    AttributeChoice,
    Attributes,
    _as_dict,
    _as_list_of_dicts,
)


class StubResponse:
    def __init__(self, data: Any) -> None:
        self.data = data

    def json(self) -> Any:
        return self.data


def _client(*responses: Any) -> tuple[Attributes, MagicMock]:
    session = MagicMock()
    session.request.side_effect = [StubResponse(response) for response in responses]
    return Attributes(session), session


def test_response_normalizers_reject_unexpected_shapes() -> None:
    assert _as_list_of_dicts(None) == []
    assert _as_list_of_dicts({"ID": 1}) == [{"ID": 1}]
    assert _as_list_of_dicts([{"ID": 1}, "ignored", {"ID": 2}]) == [
        {"ID": 1},
        {"ID": 2},
    ]
    assert _as_list_of_dicts("unexpected") == []
    assert _as_dict({"ID": 1}) == {"ID": 1}
    assert _as_dict([]) is None


def test_attribute_dtos_accept_common_id_casing() -> None:
    assert Attribute.from_dict({"Id": 4, "Name": "Department"}).ID == 4
    assert AttributeChoice.from_dict({"id": 8, "Name": "Finance", "Order": 2}) == (
        AttributeChoice(ID=8, Name="Finance", Order=2)
    )


def test_attribute_listing_methods_use_legacy_paths_and_typed_wrappers() -> None:
    client, session = _client(
        [{"ID": 1, "Name": "Application"}],
        [{"ID": 2, "Name": "Component"}],
        [{"ID": 3, "Name": "All"}],
    )

    assert client.list_for_application_component(7, "/Tickets/")[0].ID == 1
    assert client.list_for_component("/People/")[0].ID == 2
    assert client.list_all()[0].ID == 3
    assert [call.args[:2] for call in session.request.call_args_list] == [
        ("GET", "/api/applications/7/attributes/Tickets"),
        ("GET", "/api/attributes/People"),
        ("GET", "/api/attributes"),
    ]


def test_attribute_choice_lifecycle_preserves_paths_payloads_and_copy_parameter() -> None:
    client, session = _client(
        [{"ID": 10, "Name": "Original"}],
        {"ID": 11, "Name": "Copied"},
        {"ID": 11, "Name": "Edited"},
        None,
    )

    assert client.list_choices(5)[0].Name == "Original"
    assert client.add_choice(5, {"Name": "Copied"}, copy_from_choice_id=10).ID == 11
    assert client.edit_choice(5, 11, {"Name": "Edited"}).Name == "Edited"
    assert client.delete_choice(5, 11) is True
    assert session.request.call_args_list[1].kwargs == {
        "params": {"copyFromChoiceId": "10"},
        "json": {"Name": "Copied"},
    }
    assert session.request.call_args_list[2].args == (
        "PUT",
        "/api/attributes/5/choices/11",
    )
    assert session.request.call_args_list[3].args == (
        "DELETE",
        "/api/attributes/5/choices/11",
    )


def test_custom_attribute_filters_are_optional_and_use_vendor_parameter_names() -> None:
    client, session = _client([{"ID": 21, "Name": "Filtered"}], [])

    result = client.list_custom(component_id=1, associated_type_id=2, app_id=3)
    empty = client.list_custom()

    assert [attribute.ID for attribute in result] == [21]
    assert empty == []
    assert session.request.call_args_list[0].kwargs == {
        "params": {"componentId": "1", "associatedTypeId": "2", "appId": "3"}
    }
    assert session.request.call_args_list[1].kwargs == {"params": None}
