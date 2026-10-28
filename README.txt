Personal Library
================

A command-line app for tracking books, reading status, and progress. Book data
is saved in data/books.json.

Installation
------------

Install Python 3.10 or newer, then open PowerShell in the project folder and
run:

    python -m venv .venv
    .\.venv\Scripts\Activate.ps1

No extra packages are required. Run commands from the project folder with
Python:

    python -m src --help

Project structure
-----------------

    src/__main__.py       CLI arguments and command output
    src/app/manager.py    Library operations and statistics
    src/app/models.py     Book data, validation, and legacy status handling
    src/app/storage.py    JSON loading and saving
    src/app/errors.py     Application-specific exceptions
    src/app/utils.py      Shared utility functions
    src/config.py         Data-file location
    data/books.json       Saved book collection


Commands
--------

Add a book (status is optional: to-read, reading, or finished):

    python -m src add --title "The Hobbit" --author "J. R. R. Tolkien" --genre Fantasy --pages 310 --status to-read

List books, optionally filtering by status or genre:

    python -m src list
    python -m src list --status reading

Change a book's status:

    python -m src status <book_id> <to-read|reading|finished>

Update progress for a book marked as reading:

    python -m src progress <book_id> <current_page>

Mark a book as finished:

    python -m src finish <book_id>

Remove a book:

    python -m src remove <book_id>

Search book titles and authors:

    python -m src search "hobbit" or python -m src search "J."

Show collection statistics:

    python -m src stats

Use the ID shown by the list command for status, progress, finish, and remove.
