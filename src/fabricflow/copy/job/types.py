from enum import Enum


class SourceType(Enum):
    """Enum for different types of data sources."""

    SQL_SERVER = "SQLServer"


class SinkType(Enum):
    """Enum for different types of data sinks."""

    LAKEHOUSE_TABLE = "LakehouseTable"
    PARQUET_FILE = "ParquetFile"
