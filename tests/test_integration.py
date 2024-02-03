"""Integration or end-to-end tests for pubber.

Mainly these involve invoking entry-point-level functions and verifying the output.
"""
import io
import json

from typing import Any, Mapping

import pubber

from . import TEST_ASSETS_DIR


def assert_object_type(subject: Mapping[str, Any], object_type: str) -> None:
    """Asserts that `subject` is an AcitivityPub object of type `object_type`."""
    assert "@context" in subject
    assert subject["@context"] == "https://www.w3.org/ns/activitystreams"
    assert "id" in subject
    assert isinstance(subject["id"], str)
    assert "type" in subject
    assert subject["type"] == object_type


def test_json() -> None:
    """Invoking `publish` with a directory path and public key produces a file containing a valid
    JSON-LD ActivityPub document.
    """
    output_stream = io.StringIO()

    with open(TEST_ASSETS_DIR / "id_rsa.pub") as public_key:
        pubber.publish(TEST_ASSETS_DIR / "posts", public_key, output_stream)

    str_result = output_stream.getvalue()
    result = json.loads(str_result)

    assert_object_type(result, "OrderedCollection")
    assert result["id"] == "https://example.com/outbox-id"
    assert "totalItems" in result
    assert result["totalItems"] == 2
    assert "orderedItems" in result
    assert isinstance(result["orderedItems"], list)
    assert len(result["orderedItems"]) == 2

    for i, item in enumerate(result["orderedItems"]):
        assert_object_type(item, "Create")
        assert item["id"] == "https://example.com/create-id"
        assert "actor" in item
        assert "object" in item
        assert isinstance(item["object"], dict)

        obj = item["object"]
        assert "id" in obj
        assert obj["id"] == f"https://example.com/test-id-{i}"
        assert "type" in obj
        assert obj["type"] == "Note"
        assert "published" in obj
        assert obj["published"] == "2024-02-03T10:22:19Z"
        assert "attributedTo" in obj
        assert obj["attributedTo"] == "https://example.com/actor"
        assert "content" in obj
        assert obj["content"] == "My Test Post\nhttps://example.com/test-post.html"
        assert "to" in obj
        assert obj["to"] == "https://www.w3.org/ns/activitystreams#Public"
