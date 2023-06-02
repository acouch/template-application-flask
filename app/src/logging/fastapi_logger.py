"""Module for adding standard logging functionality to a FastAPI app.

This is starlette middleware for logging inspired by https://github.com/jeffsiver/fastapi-route-logger/

"""
import logging
import re
import time
import typing
from typing import Callable

from fastapi import FastAPI, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

class FastAPILoggerMiddleware(BaseHTTPMiddleware):
    def __init__(
        self,
        app: FastAPI,
        *,
        logger: typing.Optional[logging.Logger] = None,
        skip_routes: typing.List[str] = None,
        skip_regexes: typing.List[str] = None,
    ):
        self._logger = logger if logger else logging.getLogger(__name__)
        self._skip_routes = skip_routes if skip_routes else []
        self._skip_regexes = (
            list(map(lambda regex: re.compile(regex), skip_regexes))
            if skip_regexes
            else []
        )
        super().__init__(app)

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if self._should_route_be_skipped(request):
            return await call_next(request)

        return await self._execute_request_with_logging(request, call_next)

    def _should_route_be_skipped(self, request: Request) -> bool:
        return any(
            [True for path in self._skip_routes if request.url.path.startswith(path)]
            + [True for regex in self._skip_regexes if regex.match(request.url.path)]
        )

    async def _execute_request_with_logging(
        self, request: Request, call_next: Callable
    ) -> Response:
        # Add handlers
        start_time = time.perf_counter()
        self._logger.info(f"start request {start_time}")
        await self._logger.info("request log", request=request)

        response = await self._execute_request(call_next, request)
        await self._logger.info("response log", response=response)

        finish_time = time.perf_counter()
        self._logger.info(
            self._generate_success_log(request, response, finish_time - start_time)
        )

        return response

    def _generate_success_log(
        self, request: Request, response: Response, execution_time: float
    ):
        extra={
            "response.status_code": response.status_code,
            "response.content_length": response.content_length,
            "response.content_type": response.content_type,
            "response.mimetype": response.mimetype,
            "response.time_ms": execution_time * 1000,
        },
        return "end request", extra

    async def _execute_request(self, call_next: Callable, request: Request) -> Response:
        try:
            response = await call_next(request)
        except Exception:
            self._logger.exception(
                f"Request failed with exception {request.url.path}, method={request.method}"
            )
            raise
        return response