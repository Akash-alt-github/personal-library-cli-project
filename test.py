"""Basic tests for the personal library application."""

import tempfile
import unittest
from pathlib import Path

from src.app.errors import BookNotFound
from src.app.manager import LibraryManager
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

