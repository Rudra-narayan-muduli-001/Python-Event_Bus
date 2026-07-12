from __future__ import annotations
from typing import Any, Optional
from app.core.exceptions.base import AIOSError, ErrorCategory, ErrorSeverity

__all__ = [
    "DatabaseError",
    "ConnectionError",
    "TransactionError",
    "MigrationError",
    "QueryError",
    "IntegrityError",
    "BackupError",
    "EncryptionKeyError",
    "VectorStoreError",
    "KnowledgeGraphError",
]

class DatabaseError(AIOSError):
    default_category = ErrorCategory.DATABASE
    default_severity = ErrorSeverity.ERROR


class ConnectionError(DatabaseError):
    def __init__(self, backend: str, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        super().__init__(
            f"Database connection failed for backend '{backend}'",
            code="DB_CONNECTION_ERROR",
            severity=ErrorSeverity.CRITICAL,
            cause=cause,
            **kwargs,
        )
        self.with_context(backend=backend)


class TransactionError(DatabaseError):

    def __init__(self, operation: str, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        super().__init__(
            f"Transaction failed during '{operation}'",
            code="DB_TRANSACTION_ERROR",
            cause=cause,
            **kwargs,
        )
        self.with_context(operation=operation)


class MigrationError(DatabaseError):
    def __init__(self, version: Any, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        super().__init__(
            f"Database migration failed at version: {version}",
            code="DB_MIGRATION_ERROR",
            severity=ErrorSeverity.CRITICAL,
            recoverable=False,
            cause=cause,
            **kwargs,
        )
        self.with_context(version=str(version))


class QueryError(DatabaseError):
    def __init__(self, statement: Optional[str] = None, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        super().__init__(
            "Database query execution failed",
            code="DB_QUERY_ERROR",
            cause=cause,
            **kwargs,
        )
        if statement:
            self.with_context(statement=statement[:500])


class IntegrityError(DatabaseError):
    def __init__(self, constraint: Optional[str] = None, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        detail = f": {constraint}" if constraint else ""
        super().__init__(
            f"Database integrity constraint violated{detail}",
            code="DB_INTEGRITY_ERROR",
            cause=cause,
            **kwargs,
        )
        self.with_context(constraint=constraint)


class BackupError(DatabaseError):
    def __init__(self, operation: str = "backup", cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        super().__init__(
            f"Database {operation} operation failed",
            code="DB_BACKUP_ERROR",
            cause=cause,
            **kwargs,
        )
        self.with_context(operation=operation)


class EncryptionKeyError(DatabaseError):

    def __init__(self, reason: Optional[str] = None, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        suffix = f": {reason}" if reason else ""
        super().__init__(
            f"Encrypted database key error{suffix}",
            code="DB_ENCRYPTION_KEY_ERROR",
            severity=ErrorSeverity.FATAL,
            recoverable=False,
            cause=cause,
            **kwargs,
        )
        self.with_context(backend="sqlcipher")


class VectorStoreError(DatabaseError):

    def __init__(self, operation: str, collection: Optional[str] = None, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        super().__init__(
            f"Vector store operation '{operation}' failed",
            code="DB_VECTOR_STORE_ERROR",
            cause=cause,
            **kwargs,
        )
        self.with_context(operation=operation, collection=collection)


class KnowledgeGraphError(DatabaseError):

    def __init__(self, operation: str, cause: Optional[BaseException] = None, **kwargs: Any) -> None:
        super().__init__(
            f"Knowledge graph operation '{operation}' failed",
            code="DB_KNOWLEDGE_GRAPH_ERROR",
            cause=cause,
            **kwargs,
        )
        self.with_context(operation=operation)
