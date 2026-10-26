"""Custom exceptions raised by the personal library application."""


class InvalidData(Exception):
    """Raised when persisted or user-provided book data is invalid."""


class BookNotFound(Exception):
    """Raised when a requested book does not exist in the collection."""
