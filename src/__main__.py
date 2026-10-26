"""Command-line interface for the personal book collection."""

import argparse

from .app.manager import LibraryManager
from .app.models import Book
from .app.errors import BookNotFound, InvalidData


def build_parser() -> argparse.ArgumentParser:
    """Build the command-line parser and its subcommands."""
    parser = argparse.ArgumentParser(
        description="Manage your personal book collection."
    )
    commands = parser.add_subparsers(dest="command", required=True)

    add_parser = commands.add_parser("add", help="Add a book")
    add_parser.add_argument("--title", required=True, help="Book title")
    add_parser.add_argument(
        "--author", required=True, nargs="+", help="Book author"
    )
    add_parser.add_argument("--genre", required=True, help="Book genre")
    add_parser.add_argument("--pages", required=True, type=int, help="Total page count")
    add_parser.add_argument(
        "--status", choices=("to-read", "reading", "finished"), default="to-read"
    )

    list_parser = commands.add_parser("list", help="List books")
    list_parser.add_argument("--status", choices=("to-read", "reading", "finished"))
    list_parser.add_argument("--genre", help="Filter by genre")

    status_parser = commands.add_parser(
        "status", help="Change a book's reading status"
    )
    status_parser.add_argument("book_id", help="Book ID shown by the list command")
    status_parser.add_argument(
        "status", choices=("to-read", "reading", "finished"), help="New status"
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
    """Print matching books, including IDs for later update or removal."""
    if not books:
        print("No books found.")
        return
    for book in books:
        book_details = (
            f"{book.id} | {book.title} by {book.author} | {book.genre} | "
            f"{book.current_page}/{book.pages} pages | {book.status}"
        )
        if book.finished_date:
            book_details += f" | finished {book.finished_date}"
        print(book_details)


def main(argv: list[str] | None = None) -> int:
    """Run one library command and return an appropriate process status."""
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        library = LibraryManager()
        if args.command == "add":
            book = library.add_book(
                args.title, " ".join(args.author), args.genre, args.pages, args.status
            )
            print(f"Added '{book.title}' (ID: {book.id}).")
        elif args.command == "list":
            _print_books(library.list_books(args.status, args.genre))
        elif args.command == "status":
            book = library.update_status(args.book_id, args.status)
            print(f"Changed '{book.title}' to {book.status}.")
        elif args.command == "progress":
            book = library.update_progress(args.book_id, args.current_page)
            print(f"Updated '{book.title}' to page {book.current_page}.")
        elif args.command == "finish":
            book = library.mark_finished(args.book_id)
            print(f"Finished '{book.title}' on {book.finished_date}.")
        elif args.command == "remove":
            book = library.remove_book(args.book_id)
            print(f"Removed '{book.title}'.")
        elif args.command == "search":
            _print_books(library.search(args.query))
        elif args.command == "stats":
            stats = library.statistics()
            print(f"Total books: {stats['total_books']}")
            print(f"Finished this year: {stats['finished_this_year']}")
            print(f"Average pages per finished book: {stats['average_pages_read']:.1f}")
            print(f"Favorite genre: {stats['favorite_genre'] or 'N/A'}")
    except (BookNotFound, InvalidData, ValueError) as error:
        print(f"Error: {error}")
        return 1
    return 0

    
if __name__ == '__main__':
    raise SystemExit(main())