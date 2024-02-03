"""Unit tests for the data types in pubber.types."""

import datetime
import io
import json
import tempfile

import pytest

from pubber.types import OrderedCollection, NotesFile, NotesFileException

from tests import TEST_ASSETS_DIR
from tests.test_integration import assert_object_type


def test_ordered_collection_json() -> None:
    """`OrderedCollection.json` is a JSON-serialized version of the `OrderedCollection` object."""
    ordered_collection = OrderedCollection(
        "https://example.com",
        [
            NotesFile("Notes File 1", datetime.datetime(2024, 2, 2)),
            NotesFile("Notes File 2", datetime.datetime(2024, 2, 3)),
        ]
    )

    result = json.loads(ordered_collection.json)

    assert_object_type(result, "OrderedCollection")
    assert "orderedItems" in result
    assert len(result["orderedItems"]) == 2


def test_ordered_collection_writes() -> None:
    """`OrderedCollection.write` writes JSON to the provided stream."""
    ordered_collection = OrderedCollection(
        "https://example.com",
        [
            NotesFile("Notes File 1", datetime.datetime(2024, 2, 2)),
            NotesFile("Notes File 2", datetime.datetime(2024, 2, 3)),
        ]
    )
    stream = io.StringIO()

    ordered_collection.write(stream)
    result = json.loads(stream.getvalue())

    assert_object_type(result, "OrderedCollection")
    assert "orderedItems" in result
    assert len(result["orderedItems"]) == 2


def test_notes_file_json() -> None:
    """`NotesFile.json` is a JSON-serialized version of the `NotesFile` object."""
    result = NotesFile("Notes File", datetime.datetime(2023, 2, 3)).dict("https://example.com", 1)

    assert_object_type(result, "Create")


def test_notes_file_from_file() -> None:
    """`NotesFile.from_file` instantiates a `NotesFile` object from the front-matter in the file."""
    with open(TEST_ASSETS_DIR / "posts" / "test-note-1.md") as fp:
        notes_file = NotesFile.from_file(fp)

    assert notes_file.title == "Test Note 1"
    assert notes_file.publication_datetime == datetime.datetime(2024, 2, 2)


def test_notes_file_missing_front_matter() -> None:
    """`NotesFile.from_file` raises a `NotesFileException` if front-matter is missing."""
    with pytest.raises(NotesFileException) as exc_info, tempfile.TemporaryFile(
        "w+"
    ) as fp:
        fp.write("No front-matter\n")
        fp.seek(0)
        NotesFile.from_file(fp)

    assert "missing front-matter" in str(exc_info.value)


def test_notes_file_invalid_line() -> None:
    """`NotesFile.from_file` raises a `NotesFileException` if a front-matter line is not a key-value
    pair.
    """
    with pytest.raises(NotesFileException) as exc_info, tempfile.TemporaryFile(
        "w+"
    ) as fp:
        fp.write("---\ninvalidline\n---\n")
        fp.seek(0)
        NotesFile.from_file(fp)

    assert "Invalid key-value in front-matter" in str(exc_info.value)


def test_notes_file_bad_publication_date() -> None:
    """`NotesFile` raises a `NotesFileException` if publication_date is not an ISO8601-formatted
    date.
    """
    with pytest.raises(NotesFileException) as exc_info, tempfile.TemporaryFile(
        "w+"
    ) as fp:
        fp.write("---\npublication_date: notadate\n---\n")
        fp.seek(0)
        NotesFile.from_file(fp)

    assert "Bad publication_date" in str(exc_info.value)


def test_notes_file_sort() -> None:
    """`NotesFile` instances sort on publication date."""
    notes_file_1 = NotesFile("Notes File 1", datetime.date(2024, 2, 2))
    notes_file_2 = NotesFile("Notes File 2", datetime.date(2024, 2, 3))

    assert [notes_file_1, notes_file_2] == sorted([notes_file_2, notes_file_1])
