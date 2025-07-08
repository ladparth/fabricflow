"""
FabricFlow: A Python SDK for Microsoft Fabric Data Pipelines

FabricFlow is a comprehensive Python SDK that provides a code-first approach to building,
managing, and automating Microsoft Fabric data pipelines, workspaces, and core items.
It offers a high-level, object-oriented interface for interacting with the Microsoft
Fabric REST API.

Key Features:
- Pipeline Templates: Pre-built templates for common data integration patterns
- Pipeline Execution: Trigger, monitor, and extract results from pipeline runs
- Copy & Lookup Activities: Build and execute data pipeline activities with source/sink abstractions
- Workspace & Item Management: CRUD operations for workspaces and core Fabric items
- Connection & Capacity Utilities: Resolve and manage connections and capacities
- Service Principal Authentication: Secure authentication with Azure Service Principal credentials
- Comprehensive Logging: Built-in logging utilities for diagnostics and monitoring

Quick Start:
    ```python
    from fabricflow import create_workspace, create_data_pipeline
    from fabricflow.pipeline.templates import COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE
    from fabricflow.pipeline.activities import Copy
    from fabricflow.pipeline.sources import SQLServerSource
    from fabricflow.pipeline.sinks import LakehouseTableSink
    from sempy.fabric import FabricRestClient

    # Initialize client
    client = FabricRestClient()

    # Create workspace
    create_workspace(client, "MyWorkspace", "MyCapacity")

    # Create pipeline from template
    create_data_pipeline(
        client,
        COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE,
        "MyWorkspace"
    )

    # Execute copy operation
    copy = Copy(client, "MyWorkspace", COPY_SQL_SERVER_TO_LAKEHOUSE_TABLE)
    source = SQLServerSource("conn_id", "database", "SELECT * FROM table")
    sink = LakehouseTableSink("lakehouse", "workspace", "schema", "table", "Overwrite")
    # Execute the copy operation
    result = copy.source(source).sink(sink).execute()
    ```

Main Components:
- Pipeline Activities: Copy, Lookup
- Sources: SQLServerSource (BaseSource)
- Sinks: LakehouseTableSink, ParquetFileSink (BaseSink)
- Templates: DataPipelineTemplates enum with pre-built pipeline definitions
- Core Management: Workspaces, Items, Connections, Capacities
- Authentication: ServicePrincipalTokenProvider

For detailed documentation and examples, visit: https://github.com/ladparth/fabricflow
"""

import logging
from logging import Logger
from .log_utils import setup_logging

# Pipeline core
from .pipeline.executor import DataPipelineExecutor, DataPipelineError, PipelineStatus
from .pipeline.activities import Copy, Lookup
from .pipeline.templates import DataPipelineTemplates, get_template, get_base64_str
from .pipeline.utils import create_data_pipeline

# Pipeline sources and sinks
from .pipeline.sinks import LakehouseTableSink, ParquetFileSink, BaseSink, SinkType
from .pipeline.sources import BaseSource, SQLServerSource, SourceType

# Core items and workspaces
from .core.items.manager import FabricCoreItemsManager
from .core.items.types import FabricItemType
from .core.workspaces.utils import get_workspace_id
from .core.workspaces.manager import FabricWorkspacesManager
from .core.utils import create_workspace

# Connections and capacities
from .core.connections import resolve_connection_id
from .core.capacities import resolve_capacity_id

# Authentication
from .auth.provider import ServicePrincipalTokenProvider

# Backward compatibility for CopyManager
CopyManager = Copy

__all__: list[str] = [
    # Pipeline core
    "DataPipelineExecutor",
    "DataPipelineError",
    "PipelineStatus",
    "setup_logging",
    "DataPipelineTemplates",
    "get_template",
    "get_base64_str",
    "create_data_pipeline",
    "CopyManager",
    "Copy",
    "Lookup",
    # Pipeline sources and sinks
    "LakehouseTableSink",
    "ParquetFileSink",
    "SinkType",
    "BaseSink",
    "BaseSource",
    "SQLServerSource",
    "SourceType",
    # Core items and workspaces
    "FabricCoreItemsManager",
    "FabricItemType",
    "get_workspace_id",
    "FabricWorkspacesManager",
    "create_workspace",
    # Connections and capacities
    "resolve_connection_id",
    "resolve_capacity_id",
    # Authentication
    "ServicePrincipalTokenProvider",
]

logger: Logger = logging.getLogger(__name__)

logger.addHandler(logging.NullHandler())
