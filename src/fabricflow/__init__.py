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
