"""The main public API for pubber.

Generally invoked via the CLI, e.g., `pubber publish ...` or via import, e.g.

    import pubber

    pubber.publish(...)
"""

import heapq
import sys

from pathlib import Path
from typing import Iterable, TextIO

from .types import NotesFile, OrderedCollection


def collect_notes_files(directory: Path) -> Iterable[NotesFile]:
    """Yields publishable files from `directory` in order of publication date.
    Uses a heap because I felt like it.

    :directory: The directory from which to recursively collect iterable files.

    Impure.
    """
    stack = [directory]
    notes_files = []

    while stack:
        next_dir = stack.pop()

        for path in next_dir.iterdir():
            if path.is_dir():
                stack.append(path)
            elif path.is_file():
                with open(path) as fp:
                    notes_files.append(NotesFile.from_file(fp))

    heapq.heapify(notes_files)

    while notes_files:
        yield heapq.heappop(notes_files)


def publish(
    directory: Path, output_stream: TextIO = sys.stdout
) -> None:
    """Publishes a directory of header-marked files to a JSON-LD ActivityPub outbox document.

    :directory: The directory to recursively collect publication-ready files from.
        Should already be validated to be a directory.
    :output_stream: A path-like or file-like object to output to. Defaults to stdout.

    Impure.
    """
    notes_files = collect_notes_files(directory)
    ordered_collection = OrderedCollection("https://example.com", notes_files)
    ordered_collection.write(output_stream)
