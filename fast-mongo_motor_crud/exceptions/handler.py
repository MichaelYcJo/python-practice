from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging

VALIDATION_ERROR_CODE = 111111
UN_KNOWN_ERROR_CODE = 222222


class BaseExceptionHandler(HTTPException):
    error_code: str
    status_code: int
    message: str

    def __init__(self, custom_message: str = None, adding_message: bool = False):
        if custom_message:
            if adding_message:
                detail = f"{self.message} {custom_message}"
            else:
                detail = custom_message
        else:
            detail = self.message

        self.message = detail
        super().__init__(status_code=self.status_code, detail=self.message)


async def global_exception_handler(request: Request, exc: Exception):
    logging.error(f"[Exception] - {str(exc)}")

    if isinstance(exc, BaseExceptionHandler):
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "status_code": exc.status_code,
                "error_code": exc.error_code,
                "message": exc.message,
                "error_class": exc.__class__.__name__,
            },
        )
    elif isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=422,
            content={
                "status_code": 422,
                "error_code": VALIDATION_ERROR_CODE,
                "error_detail": exc.errors(),
                "error_class": exc.__class__.__name__,
            },
        )
    return JSONResponse(
        status_code=500,
        content={
            "error_code": "INTERNAL_SERVER_ERROR",
            "error_detail": str(exc),
            "error_class": exc.__class__.__name__,
        },
    )
