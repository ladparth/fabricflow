"""Microsoft Fabric Data Pipeline Templates."""

from enum import Enum
import base64
import os
import json
from typing import Union, Dict, Any


class DataPipelineTemplates(Enum):
    """Predefined templates for Microsoft Fabric data pipelines."""

    COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE = "CopySQLServerToLakehouseTable"
    COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE_FOR_EACH = "CopySQLServerToLakehouseTableForEach"
    COPY_SQL_SERVER_TO_PARQUET_FILE = "CopySQLServerToParquetFile"
    COPY_SQL_SERVER_TO_PARQUET_FILE_FOR_EACH = "CopySQLServerToParquetFileForEach"
    COPY_GOOGLE_BIGQUERY_TO_LAKEHOUSE_TABLE = "CopyGoogleBigQueryToLakehouseTable"
    COPY_GOOGLE_BIGQUERY_TO_PARQUET_FILE = "CopyGoogleBigQueryToParquetFile"
    COPY_POSTGRESQL_TO_LAKEHOUSE_TABLE = "CopyPostgreSQLToLakehouseTable"
    COPY_POSTGRESQL_TO_PARQUET_FILE = "CopyPostgreSQLToParquetFile"
    COPY_FILES_TO_LAKEHOUSE = "CopyFilesToLakehouse"
    LOOKUP_SQL_SERVER = "LookupSQLServer"
    LOOKUP_SQL_SERVER_FOR_EACH = "LookupSQLServerForEach"
    LOOKUP_GOOGLE_BIGQUERY = "LookupGoogleBigQuery"
    LOOKUP_POSTGRESQL = "LookupPostgreSQL"


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
COPY_GOOGLE_BIGQUERY_TO_LAKEHOUSE_TABLE = (
    DataPipelineTemplates.COPY_GOOGLE_BIGQUERY_TO_LAKEHOUSE_TABLE
)
COPY_GOOGLE_BIGQUERY_TO_PARQUET_FILE = (
    DataPipelineTemplates.COPY_GOOGLE_BIGQUERY_TO_PARQUET_FILE
)
COPY_POSTGRESQL_TO_LAKEHOUSE_TABLE = (
    DataPipelineTemplates.COPY_POSTGRESQL_TO_LAKEHOUSE_TABLE
)
COPY_POSTGRESQL_TO_PARQUET_FILE = DataPipelineTemplates.COPY_POSTGRESQL_TO_PARQUET_FILE
COPY_FILES_TO_LAKEHOUSE = DataPipelineTemplates.COPY_FILES_TO_LAKEHOUSE

# Lookup templates
LOOKUP_SQL_SERVER = DataPipelineTemplates.LOOKUP_SQL_SERVER
LOOKUP_SQL_SERVER_FOR_EACH = DataPipelineTemplates.LOOKUP_SQL_SERVER_FOR_EACH
LOOKUP_GOOGLE_BIGQUERY = DataPipelineTemplates.LOOKUP_GOOGLE_BIGQUERY
LOOKUP_POSTGRESQL = DataPipelineTemplates.LOOKUP_POSTGRESQL


def get_base64_str(source: Union[str, Dict[str, Any]]) -> str:
    """
    Convert a file path (str) or pipeline definition (dict) to a base64-encoded string.

    Args:
        source: File path (str) or pipeline definition (dict).

    Returns:
        Base64-encoded string of the content.

    Raises:
        FileNotFoundError: If the file path does not exist.
        TypeError: If source is neither str nor dict.
        json.JSONEncodeError: If the dict cannot be serialized to JSON.
    """
    if isinstance(source, str):
        # Handle file path
        if not os.path.exists(source):
            raise FileNotFoundError(f"File not found: {source}")
        if not source.lower().endswith(".json"):
            raise ValueError(f"Provided file is not a JSON file: {source}")
        with open(source, "r", encoding="utf-8") as f:
            content = f.read()
    elif isinstance(source, dict):
        # Handle JSON dictionary
        content = json.dumps(source, indent=2)
    else:
        raise TypeError(f"Expected str (file path) or dict (JSON), got {type(source)}")

    base64_bytes = base64.b64encode(content.encode("utf-8"))
    return base64_bytes.decode("utf-8")


def get_template(template: Union[DataPipelineTemplates, Dict[str, Any], str]) -> dict:
    """
    Get a pipeline template definition for Fabric REST API.

    Supports:
        - dict: pipeline JSON definition
        - DataPipelineTemplates: existing template enum
        - str: file path to template JSON

    Args:
        template: dict, DataPipelineTemplates, or str (file path).

    Returns:
        dict: Template definition for Fabric REST API.

    Raises:
        FileNotFoundError: If the template file does not exist.
    """
    if isinstance(template, DataPipelineTemplates):
        template_dir: str = os.path.join(os.path.dirname(__file__), "definitions")
        template_path: str = os.path.join(template_dir, f"{template.value}.json")

        base64_str: str = get_base64_str(template_path)
        display_name: str = template.value
    elif isinstance(template, (dict, str)):
        base64_str = get_base64_str(template)
        if isinstance(template, dict):
            display_name = template.get("name", "Untitled Pipeline")
        else:  # template is a file path (str)
            display_name = os.path.splitext(os.path.basename(template))[
                0
            ]  # Extract file name without extension

    else:
        raise TypeError(
            f"Expected DataPipelineTemplates, dict, or str, got {type(template)}. "
            f"Dict can be pipeline definition and str can be template file path."
        )

    return {
        "definition": {
            "parts": [
                {
                    "path": "pipeline-content.json",
                    "payload": base64_str,
                    "payloadType": "InlineBase64",
                }
            ]
        },
        "displayName": display_name,
    }
