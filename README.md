# FabricFlow

**FabricFlow** is a code-first Python SDK for building, managing, and automating Microsoft Fabric data pipelines, workspaces, and core items. It provides a high-level, object-oriented interface for interacting with the Microsoft Fabric REST API, enabling you to create, execute, and monitor data pipelines programmatically.

---

## Features

- **Pipeline Templates**: Easily create data pipelines from reusable templates (e.g., SQL Server to Lakehouse).
- **Pipeline Execution**: Trigger, monitor, and extract results from pipeline runs.
- **Copy Activities**: Build and execute copy activities with source/sink abstractions.
- **Workspace & Item Management**: CRUD operations for workspaces and core items.
- **Connection & Capacity Utilities**: Resolve and manage connections and capacities.
- **Logging Utilities**: Simple logging setup for consistent diagnostics.

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
import fabricflow as ff
from sempy.fabric import FabricRestClient
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
ff.create_workspace(fabric_client, workspace_name, capacity_name)
```

### 5. Deploy Data Pipeline Templates
You can also create individual data pipeline templates by selecting specific templates from the list.
```python
for template in ff.DataPipelineTemplates:
    ff.create_data_pipeline(
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

#### Option 1: Single Item Per Pipeline Run

```python

copy = ff.CopyManager(
    fabric_client,
    workspace_name,
    ff.DataPipelineTemplates.COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE.value
)

source = ff.SQLServerSource(
    source_connection_id=SOURCE_CONNECTION_ID,
    source_database_name=SOURCE_DATABASE_NAME,
    source_query=ITEMS_TO_LOAD[0]["source_query"],
)

sink = ff.LakehouseTableSink(
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
copy = ff.CopyManager(
    fabric_client,
    workspace_name,
    ff.DataPipelineTemplates.COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE_FOR_EACH.value
)

source = ff.SQLServerSource(
    source_connection_id=SOURCE_CONNECTION_ID,
    source_database_name=SOURCE_DATABASE_NAME,
)

sink = ff.LakehouseTableSink(
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

---

## API Overview

Below are the main classes and functions available in FabricFlow:

- `DataPipelineExecutor` – Execute data pipelines.
- `DataPipelineError` – Exception class for pipeline errors.
- `PipelineStatus` – Enum for pipeline run statuses.
- `CopyActivityExecutor` – Execute copy activity pipeline.
- `setup_logging` – Configure logging for diagnostics.
- `FabricCoreItemsManager` – Manage core Fabric items via APIs.
- `get_workspace_id` – Get a workspace ID or return the current one if not specified.
- `FabricWorkspacesManager` – Manage Fabric workspaces via APIs.
- `FabricItemType` – Enum for Fabric item types.
- `DataPipelineTemplates` – Enum for pipeline templates.
- `get_template` – Retrieve a pipeline template.
- `get_base64_str` – Utility for base64 encoding
- `create_data_pipeline` – Create a new data pipeline with template
- `resolve_connection_id` – Resolve a connection by name or ID.
- `resolve_capacity_id` – Resolve a capacity by name or ID.
- `LakehouseTableSink` – Define a Lakehouse table as a sink.
- `ParquetFileSink` – Define a Parquet file as a sink.
- `SinkType` – Enum for sink types.
- `SourceType` – Enum for source types.
- `BaseSink` – Base class for sinks.
- `BaseSource` – Base class for sources.
- `CopyManager` – Orchestrates and runs copy operations using predefined templates.
- `create_workspace` – Create a new workspace and assign to a capacity.

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