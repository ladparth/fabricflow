import logging
from fabricflow.pipeline.client import DataPipelineClient  # noqa: F401
from fabricflow.copy.client import CopyActivityClient  # noqa: F401


logger = logging.getLogger(__name__)

logger.addHandler(logging.NullHandler())

logger.info("FabricFlow initialized.")
