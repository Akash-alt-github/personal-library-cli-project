"""Collection operations for managing personal reading lists."""

from datetime import date

from .errors import BookNotFound
from .models import Book
from .storage import JsonStorage


class LibraryManager:
    """Manage a collection of books and persist each change."""

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
        book = Book(title=title, author=author, genre=genre, pages=pages, status=status)
        self.books.append(book)
        self._save()
        return book

    def list_books(
        self, status: str | None = None, genre: str | None = None
    ) -> list[Book]:
        """Return books matching optional status and genre filters."""
        matching_books = []
        for book in self.books:
            if status is not None and book.status != status:
                continue
            if genre is not None and book.genre.casefold() != genre.casefold():
                continue
            matching_books.append(book)
        return matching_books

    def search(self, query: str) -> list[Book]:
        """Find books whose title or author partially matches a query."""
        normalized_query = query.casefold()
        matching_books = []
        for book in self.books:
            title_matches = normalized_query in book.title.casefold()
            author_matches = normalized_query in book.author.casefold()
            if title_matches or author_matches:
                matching_books.append(book)
        return matching_books

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
        finished_books = []
        finished_this_year = 0
        pages_read = 0
        genre_counts: dict[str, int] = {}

        for book in self.books:
            if book.status != "finished":
                continue
            finished_books.append(book)
            pages_read += book.pages
            if book.finished_date:
                finish_year = date.fromisoformat(book.finished_date).year
                if finish_year == date.today().year:
                    finished_this_year += 1
            genre_counts[book.genre] = genre_counts.get(book.genre, 0) + 1

        favorite_genre = None
        largest_genre_count = 0
        for genre, count in genre_counts.items():
            if count > largest_genre_count:
                favorite_genre = genre
                largest_genre_count = count

        average_pages_read = 0.0
        if finished_books:
            average_pages_read = pages_read / len(finished_books)

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


