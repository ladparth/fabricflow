import logging
from logging import Logger
from .log_utils import setup_logging
from .pipeline.executor import DataPipelineExecutor, DataPipelineError, PipelineStatus
from .copy.executor import CopyActivityExecutor
from .core.items.manager import FabricCoreItemsManager
from .core.workspaces.utils import get_workspace_id
from .core.workspaces.manager import FabricWorkspacesManager
from .core.items.types import FabricItemType
from .pipeline.templates import DataPipelineTemplates, get_template, get_base64_str
from .pipeline.utils import create_data_pipeline
from .core.connections import resolve_connection_id
from .core.capacities import resolve_capacity_id
from .pipeline.sinks import LakehouseTableSink, ParquetFileSink, BaseSink, SinkType
from .pipeline.sources import BaseSource, SQLServerSource, SourceType
from .copy.manager import CopyManager
from .core.utils import create_workspace
from .auth.provider import ServicePrincipalTokenProvider

__all__: list[str] = [
    "DataPipelineExecutor",
    "DataPipelineError",
    "PipelineStatus",
    "CopyActivityExecutor",
    "setup_logging",
    "FabricCoreItemsManager",
    "get_workspace_id",
    "FabricWorkspacesManager",
    "FabricItemType",
    "DataPipelineTemplates",
    "get_template",
    "get_base64_str",
    "create_data_pipeline",
    "resolve_connection_id",
    "resolve_capacity_id",
    "LakehouseTableSink",
    "ParquetFileSink",
    "SinkType",
    "SourceType",
    "BaseSink",
    "BaseSource",
    "SQLServerSource",
    "CopyManager",
    "create_workspace",
    "ServicePrincipalTokenProvider",
]

logger: Logger = logging.getLogger(__name__)

logger.addHandler(logging.NullHandler())
