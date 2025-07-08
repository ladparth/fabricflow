"""
Microsoft Fabric Data Pipeline Templates.

This module provides pre-built pipeline templates for common data integration
scenarios in Microsoft Fabric. Templates are stored as JSON files and can be
used to quickly create data pipelines for specific source-to-sink patterns.

Classes:
    DataPipelineTemplates: Enum containing all available pipeline templates.

Functions:
    get_template: Retrieve a template definition ready for Fabric API.
    get_base64_str: Utility function to encode template files as base64.

Template Categories:
    - Copy Activities: SQL Server to Lakehouse/Parquet with single or batch processing
    - Lookup Activities: SQL Server lookup operations with optional ForEach loops

All templates support parameterization for connection details, source queries,
and sink configurations.
"""

from enum import Enum
import base64
import os


class DataPipelineTemplates(Enum):
    """
    Enum for Microsoft Fabric data pipeline templates.

    This enum contains predefined templates for creating data pipelines.
    """

    COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE = "CopySQLServerToLakehouseTable"
    COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE_FOR_EACH = "CopySQLServerToLakehouseTableForEach"
    COPY_SQL_SERVER_TO_PARQUET_FILE = "CopySQLServerToParquetFile"
    COPY_SQL_SERVER_TO_PARQUET_FILE_FOR_EACH = "CopySQLServerToParquetFileForEach"
    LOOKUP_SQL_SERVER = "LookupSQLServer"
    LOOKUP_SQL_SERVER_FOR_EACH = "LookupSQLServerForEach"


# Exporting the templates individually for convenience
COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE = (
    DataPipelineTemplates.COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE
)
COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE_FOR_EACH = (
    DataPipelineTemplates.COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE_FOR_EACH
)
COPY_SQL_SERVER_TO_PARQUET_FILE = DataPipelineTemplates.COPY_SQL_SERVER_TO_PARQUET_FILE
COPY_SQL_SERVER_TO_PARQUET_FILE_FOR_EACH = (
    DataPipelineTemplates.COPY_SQL_SERVER_TO_PARQUET_FILE_FOR_EACH
)
LOOKUP_SQL_SERVER = DataPipelineTemplates.LOOKUP_SQL_SERVER
LOOKUP_SQL_SERVER_FOR_EACH = DataPipelineTemplates.LOOKUP_SQL_SERVER_FOR_EACH


def get_base64_str(file_path: str) -> str:
    """
    Reads a file and returns its base64-encoded string.

    Args:
        file_path (str): Path to the file.

    Returns:
        str: Base64-encoded string of the file content.
    Raises:
        FileNotFoundError: If the file does not exist.
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")
    with open(file_path, "r", encoding="utf-8") as f:
        content: str = f.read()
    base64_bytes: bytes = base64.b64encode(content.encode("utf-8"))
    return base64_bytes.decode("utf-8")


def get_template(template: DataPipelineTemplates) -> dict:
    """
    Get the base64-encoded template definition for a specific data pipeline template, formatted for Fabric REST API.

    Args:
        template (DataPipelineTemplates): The data pipeline template.

    Returns:
        dict: The template definition as a dict with the correct 'definition' structure for Fabric REST API.
    Raises:
        FileNotFoundError: If the template file does not exist.
    """
    template_dir: str = os.path.join(os.path.dirname(__file__), "definitions")
    template_path: str = os.path.join(template_dir, f"{template.value}.json")

    base64_str: str = get_base64_str(template_path)

    return {
        "definition": {
            "parts": [
                {
                    "path": "pipeline-content.json",
                    "payload": base64_str,
                    "payloadType": "InlineBase64",
                }
            ]
        }
    }
