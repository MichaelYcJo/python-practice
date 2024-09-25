from fastapi import status

from exceptions.handler import BaseExceptionHandler


class PostExceptions:
    class NotFoundPost(BaseExceptionHandler):
        error_code = 10001
        status_code = status.HTTP_404_NOT_FOUND
        message = "Post not found"
