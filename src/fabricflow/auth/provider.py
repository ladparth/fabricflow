"""Authentication providers for Microsoft Fabric REST API."""

from azure.identity import ClientSecretCredential
from azure.core.credentials import AccessToken
import logging
from logging import Logger
from typing import Literal
from .base import BaseTokenProvider
import warnings

logger: Logger = logging.getLogger(__name__)

SCOPE_MAPPING = {
    "pbi": "https://analysis.windows.net/powerbi/api/.default",
    "storage": "https://storage.azure.com/.default",
    "sql": "https://database.windows.net/.default",
}


def get_token(audience: Literal["pbi", "storage", "sql"]) -> str:
    """
    Get token of the specified audience using DefaultAzureCredential or notebookutils.

    Args:
        audience (Literal["pbi", "storage", "sql"]): The target audience for the token.
    Raises:
        ValueError: If audience is not supported.
        RuntimeError: If unable to obtain token from the environment.

    Returns:
        str: The access token.
    """
    if audience not in ("pbi", "storage", "sql"):
        raise ValueError(f"Invalid token audience: {audience}")
    try:
        import notebookutils  # type: ignore

        token = notebookutils.credentials.getToken(
            SCOPE_MAPPING[audience].rstrip("/.default")
        )
        return token  # Expiry is not provided by notebookutils
    except ImportError:
        try:
            from azure.identity import DefaultAzureCredential

            credential = DefaultAzureCredential()
            scope = SCOPE_MAPPING[audience]
            return credential.get_token(scope).token
        except Exception as e:
            logger.error("Failed to obtain token using DefaultAzureCredential: %s", e)
            raise RuntimeError(
                "Failed to obtain Azure authentication token. "
                "This usually means no valid authentication method is configured. "
                "Try one of the following solutions:\n"
                "1. Run 'az login' to authenticate via Azure CLI\n"
                "2. Run 'Connect-AzAccount' to authenticate via Azure PowerShell\n"
                "3. Set environment variables for Service Principal authentication\n"
                "4. Configure managed identity if running in Azure\n\n"
                f"Original error: {str(e)}"
            ) from e


class TokenAcquisitionError(Exception):
    """Raised when token acquisition fails."""


class ServicePrincipalTokenProvider(BaseTokenProvider):
    """
    Token provider for Service Principal authentication with Microsoft Fabric REST API.

    This class provides authentication tokens using Azure Service Principal credentials
    that can be used with the FabricRestClient from Sempy. It implements the TokenProvider
    interface and supports multiple audiences (Power BI, Storage, SQL).

    The provider uses Azure's ClientSecretCredential to authenticate and obtain
    access tokens for the specified scopes.

    Attributes:
        tenant_id (str): Azure Active Directory tenant ID.
        client_id (str): Azure application (client) ID.
        client_secret (str): Azure application client secret.
        SCOPE_MAPPING (dict): Mapping of audience names to OAuth scopes.

    Example:
        >>> provider = ServicePrincipalTokenProvider(
        ...     tenant_id="your-tenant-id",
        ...     client_id="your-client-id",
        ...     client_secret="your-client-secret"
        ... )
        >>> token = provider("pbi")  # Get Power BI token
        >>>
        >>> # Use with FabricRestClient
        >>> from sempy.fabric import FabricRestClient
        >>> client = FabricRestClient(token_provider=provider)
    """

    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
    ):
        """
        Initialize the ServicePrincipalTokenProvider with Service Principal credentials.

        Args:
            tenant_id: Azure tenant ID.
            client_id: Azure client ID.
            client_secret: Azure client secret.

        Raises:
            ValueError: If any required credentials are missing.
        """
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret

        if not all([self.tenant_id, self.client_id, self.client_secret]):
            logger.error("Missing required Service Principal credentials.")
            raise ValueError(
                "Missing required Service Principal credentials. "
                "Provide tenant_id, client_id, and client_secret as parameters."
            )

        logger.debug(
            "Initializing ClientSecretCredential for tenant_id=%s, client_id=%s",
            self.tenant_id,
            self.client_id,
        )
        self._credential = ClientSecretCredential(
            tenant_id=self.tenant_id,
            client_id=self.client_id,
            client_secret=self.client_secret,
        )
        logger.info("ServicePrincipalTokenProvider initialized.")

    def get_access_token(self, scope: str = SCOPE_MAPPING["pbi"]) -> AccessToken:
        """
        Get the full AccessToken object for the specified scope.

        Args:
            scope: The target scope for the token.

        Raises:
            ValueError: If scope is not specified.
            TokenAcquisitionError: If token acquisition fails.

        Returns:
            AccessToken: The access token object with token and expiration info.
        """
        warnings.warn(
            "get_access_token is deprecated and will be removed in a future version. "
            "Use the __call__ method instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        if not scope:
            logger.error("Scope must be specified to acquire token.")
            raise ValueError("Scope must be specified to acquire token")

        try:
            logger.debug("Requesting AccessToken object for scope: %s", scope)
            return self._credential.get_token(scope)
        except Exception as e:
            logger.exception(
                "Failed to acquire access token for scope '%s': %s", scope, str(e)
            )
            raise TokenAcquisitionError(
                f"Failed to acquire access token for scope '{scope}': {str(e)}"
            ) from e

    def __call__(self, audience: Literal["pbi", "storage", "sql"] = "pbi") -> str:
        """
        Get an access token for the specified audience.

        Args:
            audience (Literal["pbi", "storage", "sql"]): The target audience for the token.

        Raises:
            ValueError: If audience is not supported.
            TokenAcquisitionError: If token acquisition fails.

        Returns:
            str: The access token.
        """
        if audience not in SCOPE_MAPPING:
            logger.error("Unsupported audience: %s", audience)
            raise ValueError(
                f"Unsupported audience: {audience}. Must be one of: {list(SCOPE_MAPPING.keys())}"
            )

        scope = SCOPE_MAPPING[audience]

        try:
            logger.debug("Requesting token for audience: %s", audience)
            token: AccessToken = self._credential.get_token(scope)
            return token.token
        except Exception as e:
            logger.exception(
                "Failed to acquire token for audience '%s': %s", audience, str(e)
            )
            raise TokenAcquisitionError(
                f"Failed to acquire token for audience '{audience}': {str(e)}"
            ) from e


class DefaultTokenProvider(BaseTokenProvider):
    """
    Token provider that acquires an auth token from the environment.

    Uses notebookutils in Fabric notebooks or DefaultAzureCredential elsewhere.
    Designed for local development and testing.
    """

    def __init__(self):
        """
        Initialize the DefaultTokenProvider.
        No credentials are required; relies on environment configuration.
        """
        logger.info("DefaultTokenProvider initialized.")

    def __call__(self, audience: Literal["pbi", "storage", "sql"] = "pbi") -> str:
        """
        Get an access token for the specified audience.

        Args:
            audience: The target audience for the token ("pbi", "storage", or "sql").

        Raises:
            ValueError: If audience is not supported.
            TokenAcquisitionError: If token acquisition fails.

        Returns:
            str: The access token.
        """
        if audience not in SCOPE_MAPPING:
            logger.error("Unsupported audience: %s", audience)
            raise ValueError(
                f"Unsupported audience: {audience}. Must be one of: {list(SCOPE_MAPPING.keys())}"
            )
        try:
            logger.debug("Requesting token for audience: %s", audience)
            return get_token(audience=audience)
        except Exception as e:
            logger.exception(
                "Failed to acquire token for audience '%s': %s", audience, str(e)
            )
            raise TokenAcquisitionError(
                f"Failed to acquire token for audience '{audience}': {str(e)}"
            ) from e
