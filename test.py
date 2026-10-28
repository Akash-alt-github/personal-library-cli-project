"""Basic tests for the personal library application."""

import json
import tempfile
import unittest
from pathlib import Path

from src.app.errors import BookNotFound
from src.app.manager import LibraryManager
from src.app.models import Book
from src.app.storage import JsonStorage


class LibraryManagerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        storage = JsonStorage(Path(self.temp_dir.name) / "books.json")
        self.library = LibraryManager(storage)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_add_list_and_search_books(self) -> None:
        first_book = self.library.add_book(
            "The Hobbit",
            "J. R. R. Tolkien",
            "Fantasy",
            310,
        )
        self.library.add_book("Dune", "Frank Herbert", "Science Fiction", 412)

        self.assertEqual(
            [book.title for book in self.library.list_books()],
            ["The Hobbit", "Dune"],
        )
        self.assertEqual(self.library.list_books(genre="fantasy"), [first_book])
        self.assertEqual(self.library.search("TOLKIEN"), [first_book])

    def test_progress_and_finished_status(self) -> None:
        book = self.library.add_book(
            "The Hobbit",
            "J. R. R. Tolkien",
            "Fantasy",
            310,
            "reading",
        )

        self.library.update_progress(book.id, 120)
        self.assertEqual(book.current_page, 120)

        self.library.mark_finished(book.id)
        self.assertEqual(book.status, "finished")
        self.assertEqual(book.current_page, book.pages)
        self.assertIsNotNone(book.finished_date)

    def test_statistics_include_finished_books_only(self) -> None:
        self.library.add_book("First", "Author", "Fantasy", 100, "finished")
        self.library.add_book("Second", "Author", "Fantasy", 300, "finished")
        self.library.add_book("Current", "Author", "Mystery", 200, "reading")

        self.assertEqual(
            self.library.statistics(),
            {
                "total_books": 3,
                "finished_this_year": 2,
                "average_pages_read": 200.0,
                "favorite_genre": "Fantasy",
            },
        )

    def test_legacy_status_is_normalized_when_loading_a_book(self) -> None:
        book = Book.from_dict(
            {
                "id": "legacy-book",
                "title": "Old Record",
                "author": "Author",
                "genre": "History",
                "pages": 120,
                "status": "read",
            }
        )

        self.assertEqual(book.status, "finished")
        self.assertEqual(book.current_page, 120)

    def test_duplicate_book_ids_are_made_unique_when_loaded(self) -> None:
        storage = self.library.storage
        storage.path.write_text(
            json.dumps(
                [
                    {
                        "id": "duplicate",
                        "title": "First",
                        "author": "Author",
                        "genre": "Fantasy",
                        "pages": 100,
                    },
                    {
                        "id": "duplicate",
                        "title": "Second",
                        "author": "Author",
                        "genre": "Fantasy",
                        "pages": 100,
                    },
                ]
            ),
            encoding="utf-8",
        )

        books = storage.load()

        self.assertEqual([book.id for book in books], ["duplicate", "duplicate-2"])

    def test_books_persist_and_can_be_removed(self) -> None:
        book = self.library.add_book("Dune", "Frank Herbert", "Science Fiction", 412)
        storage = self.library.storage

        reloaded_library = LibraryManager(storage)
        self.assertEqual(reloaded_library.books[0].title, "Dune")

        removed = reloaded_library.remove_book(book.id)
        self.assertEqual(removed.id, book.id)
        self.assertEqual(reloaded_library.list_books(), [])
        self.assertEqual(LibraryManager(storage).list_books(), [])

    def test_unknown_book_raises_book_not_found(self) -> None:
        with self.assertRaises(BookNotFound):
            self.library.remove_book("missing-id")


if __name__ == "__main__":
    unittest.main()
