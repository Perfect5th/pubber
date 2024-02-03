"""Typeclasses for use inside pubber."""

import datetime
import json

from dataclasses import dataclass
from typing import Any, Dict, Iterable, TextIO

ACTIVITY_STREAMS_CONTEXT = "https://www.w3.org/ns/activitystreams"


@dataclass
class OrderedCollection:
    """An internal representation of a ActivityStreams OrderedCollection.

    https://www.w3.org/ns/activitystreams#OrderedCollection

    Can be marshalled to JSON.
    """

    domain: str
    notes_files: Iterable["NotesFile"]
    id: str = "outbox"

    @property
    def json(self) -> str:
        """Serializes this `OrderedCollection` to a JSON string."""
        obj = {
            "@context": ACTIVITY_STREAMS_CONTEXT,
            "type": "OrderedCollection",
            "id": f"{self.domain}/{self.id}",
            "orderedItems": [notes_file.dict(self.domain, i + 1) for i, notes_file in enumerate(self.notes_files)],
        }

        return json.dumps(obj)

    def write(self, stream: TextIO) -> None:
        """Writes the JSON-serialized `OrderedCollection` to `stream`."""
        stream.write(self.json)


@dataclass
class NotesFile:
    """An internal representation of an object that can be published to an ActivityPub outbox as a
    Create Activity.

    It can be generated from a file using that files "front-matter", of the format:

        ---
        title: str
        publication_date: ISO8601 date
        ---

    _N.B._ this isn't YAML and I'm not following any YAML rules here.

    Instances of `NotesFile` sort on publication date.
    """

    title: str
    publication_datetime: datetime.datetime

    def __lt__(self, other: Any) -> bool:
        """Sort on `publication_date`."""
        return self.publication_datetime < other.publication_datetime

    def dict(self, domain: str, id_num: int) -> Dict:
        """Serializes this `NotesFile` to a dictionary."""
        return {
            "@context": ACTIVITY_STREAMS_CONTEXT,
            "type": "Create",
            "id": f"{domain}/note/{id_num}",
            "object": {
                "type": "Note",
                "name": self.title,
                "content": "",
                "published": self.publication_datetime.isoformat(),
            }
        }

    @classmethod
    def from_file(cls, fp: TextIO) -> "NotesFile":
        """Generates a `NotesFile` object by reading the front-matter of `fp`.
        It's assumed that `fp` is currently positioned at the start of the buffer.

        Impure.
        """
        first_line = fp.readline().strip()

        if first_line != "---":
            raise NotesFileException("File is missing front-matter")

        fields = {}
        for line in fp:
            line = line.rstrip()

            if line == "---":
                break

            try:
                key, value = line.split(":", 1)
            except ValueError:
                raise NotesFileException(f"Invalid key-value in front-matter: '{line}'")

            fields[key] = value.strip()

        pub_date = fields.pop("publication_date", "")
        try:
            publication_datetime = datetime.datetime.fromisoformat(pub_date)
        except ValueError:
            raise NotesFileException(
                f"Bad publication_date in front-matter: '{pub_date}'"
            )

        return cls(publication_datetime=publication_datetime, **fields)


class NotesFileException(Exception):
    """An exception raised when there is a problem constructing an `NotesFile`."""
