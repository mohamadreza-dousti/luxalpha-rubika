import os

from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware


APP_KEY = os.getenv("APP_KEY")


class AppKeyMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):


        app_key = request.headers.get("x-app-key")

        if APP_KEY is None:
            return JSONResponse(
                status_code=500,
                content={"detail": "APP_KEY is not configured"}
            )

        if app_key != APP_KEY:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid app key"}
            )

        return await call_next(request)
