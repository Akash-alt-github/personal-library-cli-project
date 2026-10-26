"""Domain models for books in a personal library."""

from datetime import date

from .utils import generate_id


class Book:
    """Represent a book and its current reading progress."""

    VALID_STATUSES = ("to-read", "reading", "finished")

    def __init__(
        self,
        title: str,
        author: str,
        genre: str,
        pages: int,
        status: str = "to-read",
        current_page: int = 0,
        finished_date: str | None = None,
        book_id: str | None = None,
    ) -> None:
        """Create a book and check that its details are valid."""
        self.title = self._clean_text(title)
        self.author = self._clean_text(author)
        self.genre = self._clean_text(genre)
        self.pages = pages
        self.status = self._normalize_status(status)
        self.current_page = current_page
        self.finished_date = finished_date
        self.id = book_id or generate_id()

        self._validate_fields()

        if self.status == "finished":
            self.current_page = self.pages
            if self.finished_date is None:
                self.finished_date = date.today().isoformat()
        elif self.status == "to-read":
            self.current_page = 0
            self.finished_date = None

    @staticmethod
    def _clean_text(value: str) -> str:
        """Trim whitespace from text fields."""
        return value.strip()

    @staticmethod
    def _normalize_status(status: str) -> str:
        """Normalize older status names to the current status values."""
        normalized_status = status.strip().lower()
        if normalized_status == "unread":
            return "to-read"
        if normalized_status == "read":
            return "finished"
        return normalized_status

    def _validate_fields(self) -> None:
        """Check that the book data is valid before saving."""
        if not self.title or not self.author or not self.genre:
            raise ValueError("Title, author, and genre must not be blank.")
        if self.pages <= 0:
            raise ValueError("Total pages must be greater than zero.")
        if self.status not in self.VALID_STATUSES:
            raise ValueError("Status must be to-read, reading, or finished.")
        if not 0 <= self.current_page <= self.pages:
            raise ValueError("Current page must be between zero and total pages.")

    def to_dict(self) -> dict[str, object]:
        """Return the book details as a dictionary for JSON storage."""
        return {
            "id": self.id,
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "pages": self.pages,
            "status": self.status,
            "current_page": self.current_page,
            "finished_date": self.finished_date,
        }

    @classmethod
    def from_dict(cls, data: dict[str, object]) -> "Book":
        """Create a book from a saved JSON record."""
        title = data["title"]
        author = data["author"]
        genre = data["genre"]
        pages = int(data.get("pages", data.get("total_pages", 0)))
        status = str(data.get("status", "to-read"))
        current_page = int(data.get("current_page", 0))
        finished_date = (
            str(data["finished_date"])
            if data.get("finished_date") is not None
            else None
        )
        book_id = str(data["id"]) if data.get("id") else None

        return cls(
            title=str(title),
            author=str(author),
            genre=str(genre),
            pages=pages,
            status=status,
            current_page=current_page,
            finished_date=finished_date,
            book_id=book_id,
        )
