"""Unit tests for public functions in pubber.api."""

import io

from unittest.mock import Mock

from pubber import api
from pubber import types

from tests import TEST_ASSETS_DIR


def test_collect_notes_files() -> None:
    """`api.collect_notes_files` yields `types.NotesFile` objects in order of publication date."""
    results = list(api.collect_notes_files(TEST_ASSETS_DIR / "posts"))

    assert len(results) == 2
    assert sorted(results) == results


def test_publish(monkeypatch) -> None:
    """`api.publish` invokes `api.collect_notes_files` with the given directory, instantiates a
    `types.OrderedCollection` with the result, and calls its `write` method with the output stream.
    """
    mock_notes_files_iter = iter(
        [
            types.NotesFile("Test Note 1", "2024-02-02"),
            types.NotesFile("Test Note 2", "2024-02-03"),
        ]
    )

    def mock_collect(directory):
        assert directory == TEST_ASSETS_DIR / "posts"

        return mock_notes_files_iter

    ordered_collection_mock = Mock(spec_set=types.OrderedCollection)
    ordered_collection_class_mock = Mock(
        spec_set=type, return_value=ordered_collection_mock
    )

    monkeypatch.setattr(api, "collect_notes_files", mock_collect)
    monkeypatch.setattr(api, "OrderedCollection", ordered_collection_class_mock)

    output_stream = io.StringIO()

    with open(TEST_ASSETS_DIR / "id_rsa.pub") as id_rsa_pub:
        api.publish(TEST_ASSETS_DIR / "posts", id_rsa_pub, output_stream)

    ordered_collection_class_mock.assert_called_once_with(mock_notes_files_iter)
    ordered_collection_mock.write.assert_called_once_with(output_stream)
