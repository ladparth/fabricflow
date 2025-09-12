"""Fabric REST API client implementation."""

import json
from typing import Dict
from tqdm import tqdm
import requests
from ..auth import BaseTokenProvider
from .base import BaseRestClient
from typing import Optional
import logging
import time

logger = logging.getLogger(__name__)


class FabricHTTPException(requests.HTTPError):
    """
    Raised when an API call to any Fabric REST API fails with status code >= 400.

    Parameters
    ----------
    response : requests.Response
        Response object returned from API call.
    """

    def __init__(self, response: requests.Response):
        reason = response.reason
        if isinstance(reason, bytes):
            try:
                reason = reason.decode("utf-8")
            except UnicodeDecodeError:
                reason = reason.decode("iso-8859-1")
        msg = f"{response.status_code} {reason} for url: {response.url}"
        if response.text:
            msg += f"\nError: {response.text}"
        if response.headers:
            msg += f"\nHeaders: {response.headers}"
        super().__init__(msg, response=response)


class FabricRestClient(BaseRestClient):

    def __init__(
        self,
        token_provider: Optional[BaseTokenProvider] = None,
        retry_config: Dict | None = None,
    ):
        super().__init__(token_provider, retry_config)

    def _get_base_url(self) -> str:
        return "https://api.fabric.microsoft.com/"

    def get_paged(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        **kwargs,
    ) -> list:
        """
        GET request to the Fabric REST API that handles pagination.

        Parameters
        ----------
        endpoint : str
            The relative path to the resource or the full url.
            If it's relative, the base URL is automatically prepended.
        params : dict, default=None
            Query parameters to be included in the request.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        list
            The list of items from the response.
        """

        response = self.get(endpoint, params=params, **kwargs)

        if response.status_code != 200:
            raise FabricHTTPException(response)

        items = []
        while True:
            response_json = response.json()
            items.extend(response_json["value"])

            continuation_uri = response_json.get("continuationUri")

            if continuation_uri is None:
                break

            response = self.get(continuation_uri, **kwargs)
            if response.status_code != 200:
                raise FabricHTTPException(response)

        return items

    def _get_operation_status(self, operation_id: str, **kwargs) -> Dict:
        """
        GET request to check the status of an operation.

        Parameters
        ----------
        operation_id : str
            The ID of the operation to check.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        dict
            The status of the operation.
        """

        endpoint = f"v1/operations/{operation_id}"
        response = self.get(endpoint, **kwargs)

        if response.status_code != 200:
            raise FabricHTTPException(response)

        return response.json()

    def _get_operation_result(self, operation_id: str, **kwargs) -> requests.Response:
        """
        Helper method to get the result of a long-running operation.

        Parameters
        ----------
        operation_id : str
            The ID of the operation to check.
        **kwargs : dict
            Arguments passed to the request method.

        Returns
        -------
        dict
            The result of the operation.
        """

        endpoint = f"v1/operations/{operation_id}/result"
        response = self.get(endpoint, **kwargs)

        if response.status_code != 200:
            raise FabricHTTPException(response)

        return response

    def _handle_lro(
        self, op_name: str, response: requests.Response
    ) -> requests.Response:
        """
        Handles a long-running operation by polling for its status
        and retrieving the result upon completion, showing a progress bar.

        Args:
            op_name (str): The name of the operation.
            response (requests.Response): The initial response that
                                                  triggered the LRO.

        Returns:
            requests.Response: The final result of the long-running operation.
        """
        if "x-ms-operation-id" not in response.headers:
            raise ValueError(
                "Header 'x-ms-operation-id' not found in the response for LRO."
            )

        operation_id = (
            response.headers.get("x-ms-operation-id")
            or response.headers["Location"].split("/")[-1]
        )
        logger.info(f"Long-running operation started with ID: {operation_id}")

        with tqdm(total=100, desc=f"Operation '{op_name}' Progress") as pbar:
            while True:
                status_data = self._get_operation_status(operation_id)
                status = status_data.get("status")
                percent_complete = status_data.get("percentComplete", 0)

                # Update progress bar
                pbar.set_description(f"Operation '{op_name}' status: {status}")
                pbar.update(percent_complete - pbar.n)  # Update to the new percentage

                if status == "Succeeded":
                    pbar.update(100 - pbar.n)  # Ensure the bar completes to 100%
                    logger.info("Operation succeeded. Fetching result...")
                    return self._get_operation_result(operation_id)
                elif status == "Failed":
                    pbar.close()
                    error_details = status_data.get("error", {})
                    logger.error(
                        f"Operation failed: {json.dumps(error_details, indent=2)}"
                    )
                    raise Exception(f"LRO failed with details: {error_details}")
                elif status in ["Undefined", "NotStarted", "Running"]:
                    retry_after = int(response.headers.get("Retry-After", 20))
                    time.sleep(retry_after)
                else:
                    pbar.close()
                    logger.error(f"Unknown operation status: {status}")
                    raise Exception(f"Unknown operation status: {status}")

    def request(
        self,
        method: str,
        endpoint: str,
        headers: Dict[str, str] | None = None,
        lro: bool = False,
        lro_op_name: Optional[str] = None,
        **kwargs,
    ) -> requests.Response:
        response = super().request(method, endpoint, headers, **kwargs)

        if not lro or response.status_code != 202:
            return response

        return self._handle_lro(lro_op_name or endpoint, response)
