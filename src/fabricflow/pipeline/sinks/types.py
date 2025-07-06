from enum import Enum


class SinkType(Enum):
    """Enum for different types of data sinks."""

    LAKEHOUSE_TABLE = "LakehouseTable"
    PARQUET_FILE = "ParquetFile"
