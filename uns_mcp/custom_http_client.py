import json
import logging
import os
from datetime import datetime
from typing import Any, Optional, Union

import httpx
from unstructured_client.httpclient import AsyncHttpClient


def log_request_params(
    logger,
    method,
    url,
    content=None,
    data=None,
    files=None,
    json_value=None,
    params=None,
    headers=None,
    cookies=None,
    timeout=None,
    extensions=None,
):
    """Logs request parameters in a formatted way."""
    logger.info("--- Request Parameters ---")
    logger.info(f"Method: {method}")
    logger.info(f"URL: {url}")

    if content is not None:
        logger.info("Content:")
        if isinstance(content, bytes):
            try:
                logger.info(content.decode("utf-8"))
            except UnicodeDecodeError:
                logger.info(content)
        else:
            logger.info(content)

    if data is not None:
        logger.info("Data:")

        if isinstance(data, dict):
            logger.info(json.dumps(data, indent=4))
        else:
            logger.info(data)

    if files is not None:
        logger.info("Files:")
        logger.info(files)

    if json_value is not None:
        logger.info("JSON:")
        logger.info(json.dumps(json_value, indent=4))

    if params is not None:
        logger.info("Params:")
        logger.info(json.dumps(params, indent=4))

    if headers is not None:
        logger.info("Headers:")
        logger.info(json.dumps(headers, indent=4))

    if cookies is not None:
        logger.info("Cookies:")
        logger.info(cookies)

    if timeout is not None:
        logger.info(f"Timeout: {timeout}")

    if extensions is not None:
        logger.info("Extensions:")
        logger.info(extensions)
    logger.info("--- End Request Parameters ---")


class CustomHttpClient(AsyncHttpClient):
    client: AsyncHttpClient

    def __init__(self, client: AsyncHttpClient):
        self.client = client
        self.log_file = os.path.abspath(
            f"unstructured-client-{datetime.now().strftime('%Y-%m-%d-%H-%M-%S')}.log",
        )  # Store absolute log path
        self.logger = logging.getLogger(__name__)  # Get logger for this module
        self.logger.setLevel(logging.INFO)  # Set default log level

        # Create file handler
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.INFO)

        # Create formatter and add it to the handler
        formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        # Add the handler to the logger
        self.logger.addHandler(file_handler)

    async def send(
        self,
        request: httpx.Request,
        *,
        stream: bool = False,
        auth: Union[
            httpx._types.AuthTypes,
            httpx._client.UseClientDefault,
            None,
        ] = httpx.USE_CLIENT_DEFAULT,
        follow_redirects: Union[bool, httpx._client.UseClientDefault] = httpx.USE_CLIENT_DEFAULT,
    ) -> httpx.Response:
        return await self.client.send(
            request,
            stream=stream,
            auth=auth,
            follow_redirects=follow_redirects,
        )

    def build_request(
        self,
        method: str,
        url: httpx._types.URLTypes,
        *,
        content: Optional[httpx._types.RequestContent] = None,
        data: Optional[httpx._types.RequestData] = None,
        files: Optional[httpx._types.RequestFiles] = None,
        json: Optional[Any] = None,
        params: Optional[httpx._types.QueryParamTypes] = None,
        headers: Optional[httpx._types.HeaderTypes] = None,
        cookies: Optional[httpx._types.CookieTypes] = None,
        timeout: Union[
            httpx._types.TimeoutTypes,
            httpx._client.UseClientDefault,
        ] = httpx.USE_CLIENT_DEFAULT,
        extensions: Optional[httpx._types.RequestExtensions] = None,
    ) -> httpx.Request:
        log_request_params(
            self.logger,
            method,
            url,
            content,
            data,
            files,
            json,
            params,
            headers,
            cookies,
            timeout,
            extensions,
        )

        return self.client.build_request(
            method,
            url,
            content=content,
            data=data,
            files=files,
            json=json,
            params=params,
            headers=headers,
            cookies=cookies,
            timeout=timeout,
            extensions=extensions,
        )
