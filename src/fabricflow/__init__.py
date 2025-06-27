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
from .copy.job.sinks.lakehouse_table import LakehouseTableSink
from .copy.job.sinks.parquet_file import ParquetFileSink
from .copy.job.types import SinkType, SourceType
from .copy.job.base import BaseSink, BaseSource
from .copy.job.sources.sql_server import SQLServerSource
from .copy.job.manager import CopyManager
from .core.utils import create_workspace

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
]

logger: Logger = logging.getLogger(__name__)

logger.addHandler(logging.NullHandler())
