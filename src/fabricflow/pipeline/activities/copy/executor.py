import logging
from logging import Logger

from ...activities.base import BaseActivityExecutor

logger: Logger = logging.getLogger(__name__)


class CopyActivityExecutor(BaseActivityExecutor):
    """
    Specialized client for pipelines that contain copy activities.

    This class extends BaseActivityExecutor to provide copy-specific functionality.
    """

    def get_activity_type(self) -> str:
        """Get the activity type name."""
        logger.debug("Returning activity type: Copy")
        return "Copy"
