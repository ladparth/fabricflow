# FabricFlow

[![PyPI version](https://img.shields.io/pypi/v/fabricflow?logo=python&logoColor=white&label=PyPI&color=2ecc40)](https://pypi.org/project/fabricflow/)
[![PyPI Downloads](https://static.pepy.tech/badge/fabricflow)](https://pepy.tech/projects/fabricflow)

---

**FabricFlow** is a code-first Python SDK for building, managing, and automating Microsoft Fabric data pipelines, workspaces, and core items. It provides a high-level, object-oriented interface for interacting with the Microsoft Fabric REST API, enabling you to create, execute, and monitor data pipelines programmatically.

---

## Features

- **Pipeline Templates**: Easily create data pipelines from reusable templates (e.g., SQL Server to Lakehouse).
- **Pipeline Execution**: Trigger, monitor, and extract results from pipeline runs.
- **Copy & Lookup Activities**: Build and execute copy and lookup activities with source/sink abstractions.
- **Modular Architecture**: Activities, sources, and sinks are organized in separate modules for better organization.
- **Workspace & Item Management**: CRUD operations for workspaces and core items.
- **Connection & Capacity Utilities**: Resolve and manage connections and capacities.
- **Logging Utilities**: Simple logging setup for consistent diagnostics.
- **Service Principal Authentication**: Authenticate securely with Microsoft Fabric REST API using Azure Service Principal credentials.

---

## Installation

```sh
pip install fabricflow
```

---

## Sample Usage

Below is a sample workflow that demonstrates how to use FabricFlow to automate workspace creation, pipeline deployment, and data copy operations in Microsoft Fabric.

### 1. Import Required Libraries

```python
from sempy.fabric import FabricRestClient
from fabricflow import create_workspace, create_data_pipeline
from fabricflow.pipeline.activities import Copy, Lookup
from fabricflow.pipeline.sources import SQLServerSource
from fabricflow.pipeline.sinks import LakehouseTableSink, ParquetFileSink
from fabricflow.pipeline.templates import (
    DataPipelineTemplates,
    COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE,
    COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE_FOR_EACH,
    LOOKUP_SQL_SERVER,
    LOOKUP_SQL_SERVER_FOR_EACH
)
```

### 2. Initialize Fabric Client

```python
fabric_client = FabricRestClient()
```

### 3. Define Workspace and Capacity

```python
capacity_name = "FabricFlow"
workspace_name = "FabricFlow"
```

### 4. Create Workspace (Optional)

You can create a new workspace, or use an existing one by specifying its name.

```python
create_workspace(fabric_client, workspace_name, capacity_name)
```

### 5. Deploy Data Pipeline Templates

You can also create individual data pipeline templates by selecting specific templates from the list.

```python
for template in DataPipelineTemplates:
    create_data_pipeline(
        fabric_client,
        template,
        workspace_name
    )
```

### 6. Define Source and Sink Details

```python
SOURCE_CONNECTION_ID = "your-source-connection-id"
SOURCE_DATABASE_NAME = "AdventureWorks2022"

SINK_WORKSPACE_ID = "your-sink-workspace-id"
SINK_LAKEHOUSE_ID = "your-sink-lakehouse-id"

ITEMS_TO_LOAD = [
    {
        "source_schema_name": "Sales",
        "source_table_name": "SalesOrderHeader",
        "source_query": "SELECT * FROM [Sales].[SalesOrderHeader]",
        "sink_table_name": "SalesOrderHeader",
        "sink_schema_name": "dbo",
        "sink_table_action": "Overwrite",
        "load_type": "Incremental",
        "primary_key_columns": ["SalesOrderID"],
        "skip": True,
        "load_from_timestamp": None,
        "load_to_timestamp": None,
    },
    # Add more items as needed...
]
```

### 7. Copy Data

You can copy data using either a single item per pipeline run (Option 1) or multiple items per pipeline run (Option 2). Choose the option that best fits your requirements.

> **Note**: The examples below uses the new `Copy` class. You can also use `CopyManager` for backward compatibility, but `Copy` is recommended for new code.

#### Option 1: Single Item Per Pipeline Run

```python
copy = Copy(
    fabric_client,
    workspace_name,
    COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE
)

source = SQLServerSource(
    source_connection_id=SOURCE_CONNECTION_ID,
    source_database_name=SOURCE_DATABASE_NAME,
    source_query=ITEMS_TO_LOAD[0]["source_query"],
)

sink = LakehouseTableSink(
    sink_workspace=SINK_WORKSPACE_ID,
    sink_lakehouse=SINK_LAKEHOUSE_ID,
    sink_table_name=ITEMS_TO_LOAD[0]["sink_table_name"],
    sink_schema_name=ITEMS_TO_LOAD[0]["sink_schema_name"],
    sink_table_action=ITEMS_TO_LOAD[0]["sink_table_action"],
)

result = (
    copy
    .source(source)
    .sink(sink)
    .execute()
)

```

#### Option 2: Multiple Items Per Pipeline Run

```python
copy = Copy(
    fabric_client,
    workspace_name,
    COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE_FOR_EACH
)

source = SQLServerSource(
    source_connection_id=SOURCE_CONNECTION_ID,
    source_database_name=SOURCE_DATABASE_NAME,
)

sink = LakehouseTableSink(
    sink_workspace=SINK_WORKSPACE_ID,
    sink_lakehouse=SINK_LAKEHOUSE_ID,
)

result = (
    copy
    .source(source)
    .sink(sink)
    .items(ITEMS_TO_LOAD)
    .execute()
)
```

### 8. Lookup Data (New Feature)

FabricFlow now supports lookup operations for data validation and enrichment:

```python
# Single lookup operation
lookup = Lookup(
    fabric_client,
    workspace_name,
    LOOKUP_SQL_SERVER
)

source = SQLServerSource(
    source_connection_id=SOURCE_CONNECTION_ID,
    source_database_name=SOURCE_DATABASE_NAME,
    source_query="SELECT COUNT(*) as record_count FROM [Sales].[SalesOrderHeader]",
)

result = (
    lookup
    .source(source)
    .execute()
)

# Multiple lookup operations
lookup_items = [
    {
        "source_query": "SELECT COUNT(*) as order_count FROM [Sales].[SalesOrderHeader]",
        "first_row_only": True,
    },
    {
        "source_query": "SELECT MAX(OrderDate) as latest_order FROM [Sales].[SalesOrderHeader]",
        "first_row_only": True,
    }
]

lookup = Lookup(
    fabric_client,
    workspace_name,
    LOOKUP_SQL_SERVER_FOR_EACH
)

result = (
    lookup
    .source(source)
    .items(lookup_items)
    .execute()
)
```

---

## API Overview

Below are the main classes and functions available in FabricFlow:

### Core Pipeline Components
- `DataPipelineExecutor` – Execute data pipelines and monitor their status.
- `DataPipelineError` – Exception class for pipeline errors.
- `PipelineStatus` – Enum for pipeline run statuses.
- `DataPipelineTemplates` – Enum for pipeline templates.
- `get_template` – Retrieve a pipeline template definition.
- `get_base64_str` – Utility for base64 encoding of template files.
- `create_data_pipeline` – Create a new data pipeline from template.

### Pipeline Activities
- `Copy` – Build and execute copy activities (replaces `CopyManager`).
- `Lookup` – Build and execute lookup activities for data validation.

### Sources and Sinks
- `SQLServerSource` – Define SQL Server as a data source.
- `BaseSource` – Base class for all data sources.
- `LakehouseTableSink` – Define a Lakehouse table as a data sink.
- `ParquetFileSink` – Define a Parquet file as a data sink.
- `BaseSink` – Base class for all data sinks.
- `SinkType` / `SourceType` – Enums for sink and source types.

### Workspace and Item Management
- `FabricCoreItemsManager` – Manage core Fabric items via APIs.
- `FabricWorkspacesManager` – Manage Fabric workspaces via APIs.
- `get_workspace_id` – Get a workspace ID or return the current one.
- `create_workspace` – Create a new workspace and assign to a capacity.
- `FabricItemType` – Enum for Fabric item types.

### Utilities
- `setup_logging` – Configure logging for diagnostics.
- `resolve_connection_id` – Resolve a connection by name or ID.
- `resolve_capacity_id` – Resolve a capacity by name or ID.
- `ServicePrincipalTokenProvider` – Handles Azure Service Principal authentication.

---

## Activities, Sources, and Sinks

FabricFlow provides a modular architecture with separate packages for activities, sources, sinks, and templates:

- **Activities**: `Copy`, `Lookup` - Build and execute pipeline activities
- **Sources**: `SQLServerSource`, `BaseSource`, `SourceType` - Define data sources
- **Sinks**: `LakehouseTableSink`, `ParquetFileSink`, `BaseSink`, `SinkType` - Define data destinations
- **Templates**: Pre-built pipeline definitions for common patterns

### Backward Compatibility

- **CopyManager → Copy**: The `CopyManager` class is now renamed to `Copy` for consistency. Existing code using `CopyManager` will continue to work (backward compatible alias), but new code should use `Copy`.

---

## Development

Read the [Contributing](CONTRIBUTING.md) file.

## License

[MIT License](LICENSE)

---

## Author

Parth Lad

[LinkedIn](https://www.linkedin.com/in/ladparth/) | [Website](https://thenavigatedata.com/)

## Acknowledgements

- [Microsoft Fabric REST API](https://learn.microsoft.com/en-us/rest/api/fabric/)
- [Sempy](https://pypi.org/project/sempy/)
