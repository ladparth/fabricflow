"""
Authentication providers for Microsoft Fabric REST API.

This module provides token providers for authenticating with Microsoft Fabric services
using Azure Service Principal credentials. It implements the TokenProvider interface
expected by Sempy's FabricRestClient.

Classes:
    ServicePrincipalTokenProvider: Provides authentication tokens using Service Principal credentials.
    TokenAcquisitionError: Custom exception for token acquisition failures.

Constants:
    PBI_SCOPE: Default Power BI API scope for token requests.
"""

from azure.identity import ClientSecretCredential
from azure.core.credentials import AccessToken
import logging
from logging import Logger
from typing import Literal
from sempy.fabric._token_provider import TokenProvider

logger: Logger = logging.getLogger(__name__)


class TokenAcquisitionError(Exception):
    """Custom exception raised when token acquisition fails.
    
    This exception is raised when the ServicePrincipalTokenProvider
    fails to acquire an access token for any reason, such as invalid
    credentials, network issues, or service availability problems.
    """


PBI_SCOPE = "https://analysis.windows.net/powerbi/api/.default"


class ServicePrincipalTokenProvider(TokenProvider):
    """Token provider for Service Principal authentication with Microsoft Fabric REST API.

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
        """Initialize the ServicePrincipalTokenProvider with Service Principal credentials.

        Args:
            tenant_id (str): Azure tenant ID.
            client_id (str): Azure client ID.
            client_secret (str): Azure client secret.

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

    # Class-level constant for audience-to-scope mapping
    SCOPE_MAPPING = {
        "pbi": PBI_SCOPE,
        "storage": "https://storage.azure.com/.default",
        "sql": "https://database.windows.net/.default",
    }

    def __call__(self, audience: Literal["pbi", "storage", "sql"] = "pbi") -> str:
        """Get an access token for the specified audience.

        This method implements the TokenProvider interface expected by Sempy.

        Args:
            audience (Literal["pbi", "storage", "sql"]): The target audience for the token.

        Raises:
            ValueError: If audience is not supported.
            TokenAcquisitionError: If token acquisition fails.

        Returns:
            str: The access token.
        """
        if audience not in self.SCOPE_MAPPING:
            logger.error("Unsupported audience: %s", audience)
            raise ValueError(
                f"Unsupported audience: {audience}. Must be one of: {list(self.SCOPE_MAPPING.keys())}"
            )

        scope = self.SCOPE_MAPPING[audience]

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

    def get_access_token(self, scope: str = PBI_SCOPE) -> AccessToken:
        """Get the full AccessToken object for the specified scope.

        Args:
            scope (str): The target scope for the token.

        Raises:
            ValueError: If scope is not specified.
            TokenAcquisitionError: If token acquisition fails.

        Returns:
            AccessToken: The access token object with token and expiration info.
        """
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
