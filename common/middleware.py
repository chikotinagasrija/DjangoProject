import uuid
import time
import logging

logger = logging.getLogger("api")

SLOW_API_THRESHOLD = 1.0  # seconds


class RequestIDMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        request_id = request.headers.get(
            "X-Request-ID",
            str(uuid.uuid4())
        )

        request.request_id = request_id

        start_time = time.perf_counter()

        response = self.get_response(request)

        execution_time = time.perf_counter() - start_time

        user_id = None

        if request.user.is_authenticated:
            user_id = str(request.user.id)

        logger.info(
            "API request | "
            "request_id=%s | "
            "user_id=%s | "
            "method=%s | "
            "endpoint=%s | "
            "status=%s | "
            "execution_time=%.4fs",
            request_id,
            user_id,
            request.method,
            request.path,
            response.status_code,
            execution_time,
        )

        if execution_time > SLOW_API_THRESHOLD:
            logger.warning(
                "Slow API | "
                "request_id=%s | "
                "method=%s | "
                "endpoint=%s | "
                "execution_time=%.4fs",
                request_id,
                request.method,
                request.path,
                execution_time,
            )

        response["X-Request-ID"] = request_id

        return response