from enum import Enum


class SourceType(Enum):
    """Enum for different types of data sources."""

    SQL_SERVER = "SQLServer"


class IsolationLevel(Enum):
    READ_COMMITTED = "ReadCommitted"
    READ_UNCOMMITTED = "ReadUncommitted"
    REPEATABLE_READ = "RepeatableRead"
    SERIALIZABLE = "Serializable"
    SNAPSHOT = "Snapshot"
