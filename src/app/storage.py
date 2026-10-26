"""JSON persistence for the personal book collection."""

import json
from pathlib import Path

from ..config import BOOK_DATA
from .errors import InvalidData
from .models import Book


class JsonStorage:
    """Load and save books in a JSON file."""

    def __init__(self, path: Path = BOOK_DATA) -> None:
        """Create storage for the given JSON file."""
        self.path = path

    def load(self) -> list[Book]:
        """Load all books, or create an empty file if needed."""
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if not self.path.exists():
            self.save([])
            return []

        try:
            with self.path.open("r", encoding="utf-8") as data_file:
                raw_records = json.load(data_file)
        except (json.JSONDecodeError, OSError) as error:
            raise InvalidData(f"Could not load book data: {error}") from error

        if not isinstance(raw_records, list):
            raise InvalidData("The book data file must contain a JSON list.")

        books: list[Book] = []
        used_ids: list[str] = []

        for record in raw_records:
            try:
                book = Book.from_dict(record)
            except (KeyError, TypeError, ValueError) as error:
                raise InvalidData(f"Invalid book data: {error}") from error

            if book.id in used_ids:
                original_id = book.id
                suffix = 2
                while f"{original_id}-{suffix}" in used_ids:
                    suffix += 1
                book.id = f"{original_id}-{suffix}"

            used_ids.append(book.id)
            books.append(book)

        return books

    def save(self, books: list[Book]) -> None:
        """Write all books to the JSON file."""
        self.path.parent.mkdir(parents=True, exist_ok=True)
        records = [book.to_dict() for book in books]

        try:
            with self.path.open("w", encoding="utf-8") as data_file:
                json.dump(records, data_file, indent=2)
        except OSError as error:
            raise InvalidData(f"Could not save book data: {error}") from error
