"""Command-line interface for the personal book collection."""

import argparse

from .app.errors import BookNotFound, InvalidData
from .app.manager import LibraryManager
from .app.models import Book


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser and its subcommands."""
    parser = argparse.ArgumentParser(
        description="Manage your personal book collection."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    valid_statuses = ("to-read", "reading", "finished")

    add_parser = commands.add_parser("add", help="Add a new book")
    add_parser.add_argument("--title", required=True, help="Book title")
    add_parser.add_argument("--author", required=True, nargs="+", help="Book author")
    add_parser.add_argument("--genre", required=True, help="Book genre")
    add_parser.add_argument("--pages", required=True, type=int, help="Total page count")
    add_parser.add_argument(
        "--status",
        choices=valid_statuses,
        default="to-read",
        help="Reading status for the new book",
    )

    list_parser = commands.add_parser("list", help="List books")
    list_parser.add_argument("--status", choices=valid_statuses, help="Filter by status")
    list_parser.add_argument("--genre", help="Filter by genre")

    status_parser = commands.add_parser(
        "status",
        help="Change a book's reading status",
    )
    status_parser.add_argument("book_id", help="Book ID shown by the list command")
    status_parser.add_argument(
        "status",
        choices=valid_statuses,
        help="New status to set",
    )

    progress_parser = commands.add_parser("progress", help="Update reading progress")
    progress_parser.add_argument("book_id", help="Book ID shown by the list command")
    progress_parser.add_argument("current_page", type=int, help="Current page number")

    finish_parser = commands.add_parser("finish", help="Mark a book as finished")
    finish_parser.add_argument("book_id", help="Book ID shown by the list command")

    remove_parser = commands.add_parser("remove", help="Remove a book")
    remove_parser.add_argument("book_id", help="Book ID shown by the list command")

    search_parser = commands.add_parser("search", help="Search titles and authors")
    search_parser.add_argument("query", help="Case-insensitive partial match")

    commands.add_parser("stats", help="Show collection statistics")
    return parser


def _print_books(books: list[Book]) -> None:
    """Print matching books with IDs for later updates or removal."""
    if not books:
        print("No books found.")
        return

    for book in books:
        details = (
            f"{book.id} | {book.title} by {book.author} | {book.genre} | "
            f"{book.current_page}/{book.pages} pages | {book.status}"
        )
        if book.finished_date:
            details += f" | finished {book.finished_date}"
        print(details)


def main(argv: list[str] | None = None) -> int:
    """Run one library command and return an appropriate process status."""
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        library = LibraryManager()

        match args.command:
            case "add":
                book = library.add_book(
                    args.title,
                    " ".join(args.author),
                    args.genre,
                    args.pages,
                    args.status,
                )
                print(f"Added '{book.title}' (ID: {book.id}).")
            case "list":
                _print_books(library.list_books(args.status, args.genre))
            case "status":
                book = library.update_status(args.book_id, args.status)
                print(f"Changed '{book.title}' to {book.status}.")
            case "progress":
                book = library.update_progress(args.book_id, args.current_page)
                print(f"Updated '{book.title}' to page {book.current_page}.")
            case "finish":
                book = library.mark_finished(args.book_id)
                print(f"Finished '{book.title}' on {book.finished_date}.")
            case "remove":
                book = library.remove_book(args.book_id)
                print(f"Removed '{book.title}'.")
            case "search":
                _print_books(library.search(args.query))
            case "stats":
                stats = library.statistics()
                print(f"Total books: {stats['total_books']}")
                print(f"Finished this year: {stats['finished_this_year']}")
                print(
                    "Average pages per finished book: "
                    f"{stats['average_pages_read']:.1f}"
                )
                print(f"Favorite genre: {stats['favorite_genre'] or 'N/A'}")
    except (BookNotFound, InvalidData, ValueError) as error:
        print(f"Error: {error}")
        return 1

    return 0


if __name__ == "__main__":
    main()
