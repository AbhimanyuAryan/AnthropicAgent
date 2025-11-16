"""
HTTP-level logging wrapper for capturing raw request/response cycles.
Captures all HTTP details including headers, bodies, status codes, and timing.
"""

import httpx
import json
import time
from typing import Optional
from datetime import datetime


class LoggingTransport(httpx.BaseTransport):
    """Custom HTTP transport that logs all requests and responses."""

    def __init__(self, transport: httpx.BaseTransport, logger=None):
        """
        Initialize logging transport wrapper.

        Args:
            transport: Base httpx transport to wrap
            logger: APILogger instance for logging
        """
        self.transport = transport
        self.logger = logger
        self.request_count = 0

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        """
        Handle HTTP request with logging.

        Args:
            request: HTTP request

        Returns:
            HTTP response
        """
        self.request_count += 1
        request_id = self.request_count

        # Capture request start time
        start_time = time.time()

        # Log the raw HTTP request
        if self.logger:
            self.logger.log_http_request(
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                headers=dict(request.headers),
                body=request.content.decode('utf-8') if request.content else None
            )

        # Execute the actual request
        try:
            response = self.transport.handle_request(request)

            # Read the response content (this makes it available and allows re-reading)
            response.read()

            # Capture request end time
            elapsed_time = time.time() - start_time

            # Log the raw HTTP response
            if self.logger:
                self.logger.log_http_response(
                    request_id=request_id,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    body=response.content.decode('utf-8') if response.content else None,
                    elapsed_time=elapsed_time
                )

            return response

        except Exception as e:
            elapsed_time = time.time() - start_time

            # Log the error
            if self.logger:
                self.logger.log_http_error(
                    request_id=request_id,
                    error=str(e),
                    elapsed_time=elapsed_time
                )

            raise


class AsyncLoggingTransport(httpx.AsyncBaseTransport):
    """Async version of logging transport for async clients."""

    def __init__(self, transport: httpx.AsyncBaseTransport, logger=None):
        """
        Initialize async logging transport wrapper.

        Args:
            transport: Base httpx async transport to wrap
            logger: APILogger instance for logging
        """
        self.transport = transport
        self.logger = logger
        self.request_count = 0

    async def handle_async_request(self, request: httpx.Request) -> httpx.Response:
        """
        Handle async HTTP request with logging.

        Args:
            request: HTTP request

        Returns:
            HTTP response
        """
        self.request_count += 1
        request_id = self.request_count

        # Capture request start time
        start_time = time.time()

        # Log the raw HTTP request
        if self.logger:
            self.logger.log_http_request(
                request_id=request_id,
                method=request.method,
                url=str(request.url),
                headers=dict(request.headers),
                body=request.content.decode('utf-8') if request.content else None
            )

        # Execute the actual request
        try:
            response = await self.transport.handle_async_request(request)

            # Read the response content (this makes it available and allows re-reading)
            await response.aread()

            # Capture request end time
            elapsed_time = time.time() - start_time

            # Log the raw HTTP response
            if self.logger:
                self.logger.log_http_response(
                    request_id=request_id,
                    status_code=response.status_code,
                    headers=dict(response.headers),
                    body=response.content.decode('utf-8') if response.content else None,
                    elapsed_time=elapsed_time
                )

            return response

        except Exception as e:
            elapsed_time = time.time() - start_time

            # Log the error
            if self.logger:
                self.logger.log_http_error(
                    request_id=request_id,
                    error=str(e),
                    elapsed_time=elapsed_time
                )

            raise


def create_logging_client(logger=None, **client_kwargs) -> httpx.Client:
    """
    Create an httpx client with logging enabled.

    Args:
        logger: APILogger instance
        **client_kwargs: Additional arguments for httpx.Client

    Returns:
        Configured httpx.Client with logging
    """
    # Create base transport
    base_transport = httpx.HTTPTransport(**client_kwargs.pop('transport', {}))

    # Wrap with logging transport
    logging_transport = LoggingTransport(base_transport, logger=logger)

    # Create client with logging transport
    return httpx.Client(transport=logging_transport, **client_kwargs)


def create_async_logging_client(logger=None, **client_kwargs) -> httpx.AsyncClient:
    """
    Create an async httpx client with logging enabled.

    Args:
        logger: APILogger instance
        **client_kwargs: Additional arguments for httpx.AsyncClient

    Returns:
        Configured httpx.AsyncClient with logging
    """
    # Create base transport
    base_transport = httpx.AsyncHTTPTransport(**client_kwargs.pop('transport', {}))

    # Wrap with logging transport
    logging_transport = AsyncLoggingTransport(base_transport, logger=logger)

    # Create client with logging transport
    return httpx.AsyncClient(transport=logging_transport, **client_kwargs)
