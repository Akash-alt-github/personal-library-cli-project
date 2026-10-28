"""Collection operations for managing personal reading lists."""

from datetime import date

from .errors import BookNotFound
from .models import Book
from .storage import JsonStorage


class LibraryManager:
    """Manage a collection of books and persist each change."""

    VALID_STATUSES = ("to-read", "reading", "finished")

    def __init__(self, storage: JsonStorage | None = None) -> None:
        """Load the current collection from the configured storage."""
        self.storage = storage or JsonStorage()
        self.books = self.storage.load()

    def add_book(
        self,
        title: str,
        author: str,
        genre: str,
        pages: int,
        status: str = "to-read",
    ) -> Book:
        """Add a validated book to the collection and save it."""
        book = Book(
            title=title,
            author=author,
            genre=genre,
            pages=pages,
            status=status,
        )
        self.books.append(book)
        self._save()
        return book

    def list_books(
        self, status: str | None = None, genre: str | None = None
    ) -> list[Book]:
        """Return books matching optional status and genre filters."""
        normalized_genre = genre.casefold() if genre is not None else None
        return [
            book
            for book in self.books
            if (status is None or book.status == status)
            and (
                normalized_genre is None
                or book.genre.casefold() == normalized_genre
            )
        ]

    def search(self, query: str) -> list[Book]:
        """Find books whose title or author partially matches a query."""
        normalized_query = query.casefold()
        return [
            book
            for book in self.books
            if normalized_query in book.title.casefold()
            or normalized_query in book.author.casefold()
        ]

    def update_progress(self, book_id: str, current_page: int) -> Book:
        """Update progress for a book currently marked as reading."""
        book = self._find_book(book_id)

        if book.status != "reading":
            raise ValueError("Reading progress can only be updated for a reading book.")
        if not 0 <= current_page <= book.pages:
            raise ValueError("Current page must be between zero and total pages.")

        book.current_page = current_page
        self._save()
        return book

    def update_status(self, book_id: str, status: str) -> Book:
        """Change a book's status and keep its progress fields consistent."""
        book = self._find_book(book_id)

        if status == "finished":
            book.current_page = book.pages
            book.finished_date = date.today().isoformat()
        elif status == "to-read":
            book.current_page = 0
            book.finished_date = None
        else:
            if book.status == "finished":
                book.current_page = 0
            book.finished_date = None

        book.status = status
        self._save()
        return book

    def mark_finished(self, book_id: str) -> Book:
        """Mark a book finished and record today's date."""
        return self.update_status(book_id, "finished")

    def remove_book(self, book_id: str) -> Book:
        """Remove a book by identifier and return the removed book."""
        book = self._find_book(book_id)
        self.books.remove(book)
        self._save()
        return book

    def statistics(self) -> dict[str, int | float | str | None]:
        """Calculate collection totals and reading statistics."""
        finished_books = [book for book in self.books if book.status == "finished"]
        genre_counts: dict[str, int] = {}

        for book in finished_books:
            genre_counts[book.genre] = genre_counts.get(book.genre, 0) + 1

        finished_this_year = sum(
            1
            for book in finished_books
            if book.finished_date
            and date.fromisoformat(book.finished_date).year == date.today().year
        )

        favorite_genre = None
        largest_genre_count = 0
        for genre, count in genre_counts.items():
            if count > largest_genre_count:
                favorite_genre = genre
                largest_genre_count = count

        total_pages_read = sum(book.pages for book in finished_books)
        average_pages_read = (
            total_pages_read / len(finished_books) if finished_books else 0.0
        )

        return {
            "total_books": len(self.books),
            "finished_this_year": finished_this_year,
            "average_pages_read": average_pages_read,
            "favorite_genre": favorite_genre,
        }

    def _find_book(self, book_id: str) -> Book:
        """Return a book by ID or raise a domain-specific exception."""
        for book in self.books:
            if book.id == book_id:
                return book
        raise BookNotFound(f"No book found with ID '{book_id}'.")

    def _save(self) -> None:
        """Persist the current collection."""
        self.storage.save(self.books)
