"""Small utility functions used by the application."""

import uuid


def generate_id() -> str:
    """Return a compact, unique identifier for a book."""
    identifier = uuid.uuid4().hex
    return f"{identifier[:8]}-{identifier[-12:]}"