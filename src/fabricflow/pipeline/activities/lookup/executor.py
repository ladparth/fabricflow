import logging
from logging import Logger

from ...activities.base import BaseActivityExecutor

logger: Logger = logging.getLogger(__name__)


class LookupActivityExecutor(BaseActivityExecutor):
    """
    Specialized client for pipelines that contain lookup activities.

    This class extends BaseActivityExecutor to provide lookup-specific functionality.
    """

    def get_activity_type(self) -> str:
        """Get the activity type name."""
        logger.debug("Returning activity type: Lookup")
        return "Lookup"
