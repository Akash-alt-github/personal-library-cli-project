"""Small utility functions used by the application."""

import uuid


def generate_id() -> str:
    """Return a compact, unique identifier for a book."""
    identifier_parts = str(uuid.uuid4()).split("-")
    return f"{identifier_parts[0]}-{identifier_parts[-1]}"