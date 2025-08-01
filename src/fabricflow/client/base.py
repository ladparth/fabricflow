import requests
from abc import ABC, abstractmethod
from typing import Dict, Optional, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from fabricflow.auth import BaseTokenProvider
import logging

logger = logging.getLogger(__name__)


class BaseRestClient(ABC):
    """
    Base REST client with automatic retries, error handling, and flexible configuration.

    Parameters
    ----------
    token_provider : BaseTokenProvider
        Token provider for authentication
    retry_config : dict, optional
        Retry configuration with keys: total, backoff_factor, status_forcelist
    """

    def __init__(
        self,
        token_provider: BaseTokenProvider,
        retry_config: Optional[Dict] = None,
    ):
        self.base_url = self._get_base_url()
        self.session = requests.Session()
        self.token_provider = token_provider

        # Configure retries
        retry_config = retry_config or {}

        retry_strategy = Retry(
            total=retry_config.get("total", 3),
            allowed_methods=retry_config.get(
                "allowed_methods", ["HEAD", "GET", "POST", "PUT", "PATCH", "DELETE"]
            ),
            backoff_factor=retry_config.get("backoff_factor", 1),
            status_forcelist=retry_config.get("status_forcelist", [429, 502, 503, 504]),
        )

        # Mount the retry strategy to the session
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        logger.debug(
            f"Initialized {self.__class__.__name__} with base_url: {self.base_url}"
        )

    @abstractmethod
    def _get_base_url(self) -> str:
        """
        Return the base URL for API requests.

        Returns
        -------
        str
            Base URL for all API requests

        Raises
        ------
        NotImplementedError
            Must be implemented by subclasses
        """
        raise NotImplementedError("Subclasses must implement _get_base_url")

    def _get_headers(self) -> Dict[str, str]:
        """
        Get default headers for all requests.

        Returns
        -------
        Dict[str, str]
            Dictionary containing Authorization and Accept headers
        """
        return {
            "Authorization": f"Bearer {self.token_provider()}",
            "Accept": "application/json",
        }

    def _build_url(self, endpoint: str) -> str:
        """
        Build full URL from endpoint.

        Parameters
        ----------
        endpoint : str
            API endpoint (relative to base_url or full URL)

        Returns
        -------
        str
            Complete URL for the request
        """
        if endpoint.startswith(("https://", "http://")):
            return endpoint
        return f"{self.base_url}/{endpoint.lstrip('/')}"

    def request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Make HTTP request.

        Parameters
        ----------
        method : str
            HTTP method (GET, POST, PUT, DELETE, etc.)
        endpoint : str
            API endpoint (relative to base_url or full URL)
        headers : dict, optional
            Additional headers for this request
        **kwargs
            Additional arguments passed to requests

        Returns
        -------
        requests.Response
            Response object
        """
        url = self._build_url(endpoint)
        request_headers = self._get_headers()

        if headers:
            request_headers.update(headers)

        logger.debug(f"Making {method} request to {url}")
        if kwargs.get("json"):
            logger.debug(f"Request JSON payload size: {len(str(kwargs['json']))} chars")
        if kwargs.get("data"):
            logger.debug(f"Request data payload size: {len(str(kwargs['data']))} chars")

        try:
            response = self.session.request(
                method=method, url=url, headers=request_headers, **kwargs
            )

            logger.debug(f"Response: {response.status_code} {response.reason}")
            if response.headers.get("content-length"):
                logger.debug(
                    f"Response size: {response.headers['content-length']} bytes"
                )

            return response

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {method} {url} - {str(e)}")
            raise

    def get(
        self, endpoint: str, params: Optional[Dict] = None, **kwargs
    ) -> requests.Response:
        """
        Make GET request.

        Parameters
        ----------
        endpoint : str
            API endpoint (relative to base_url or full URL)
        params : dict, optional
            URL parameters to append to the request
        **kwargs
            Additional arguments passed to requests

        Returns
        -------
        requests.Response
            Response object
        """
        return self.request("GET", endpoint, params=params, **kwargs)

    def post(
        self,
        endpoint: str,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Make POST request.

        Parameters
        ----------
        endpoint : str
            API endpoint (relative to base_url or full URL)
        data : Any, optional
            Data to send in the body of the request
        json : Any, optional
            JSON data to send in the body of the request
        **kwargs
            Additional arguments passed to requests

        Returns
        -------
        requests.Response
            Response object
        """
        return self.request("POST", endpoint, data=data, json=json, **kwargs)

    def put(
        self,
        endpoint: str,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Make PUT request.

        Parameters
        ----------
        endpoint : str
            API endpoint (relative to base_url or full URL)
        data : Any, optional
            Data to send in the body of the request
        json : Any, optional
            JSON data to send in the body of the request
        **kwargs
            Additional arguments passed to requests

        Returns
        -------
        requests.Response
            Response object
        """
        return self.request("PUT", endpoint, data=data, json=json, **kwargs)

    def patch(
        self,
        endpoint: str,
        data: Optional[Any] = None,
        json: Optional[Any] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Make PATCH request.

        Parameters
        ----------
        endpoint : str
            API endpoint (relative to base_url or full URL)
        data : Any, optional
            Data to send in the body of the request
        json : Any, optional
            JSON data to send in the body of the request
        **kwargs
            Additional arguments passed to requests

        Returns
        -------
        requests.Response
            Response object
        """
        return self.request("PATCH", endpoint, data=data, json=json, **kwargs)

    def delete(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Make DELETE request.

        Parameters
        ----------
        endpoint : str
            API endpoint (relative to base_url or full URL)
        **kwargs
            Additional arguments passed to requests

        Returns
        -------
        requests.Response
            Response object
        """
        return self.request("DELETE", endpoint, **kwargs)

    def head(self, endpoint: str, **kwargs) -> requests.Response:
        """
        Make HEAD request.

        Parameters
        ----------
        endpoint : str
            API endpoint (relative to base_url or full URL)
        **kwargs
            Additional arguments passed to requests

        Returns
        -------
        requests.Response
            Response object
        """
        return self.request("HEAD", endpoint, **kwargs)
