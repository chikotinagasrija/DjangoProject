from rest_framework.response import Response
from rest_framework.views import exception_handler


def get_error_message(data):
    if isinstance(data, dict):
        if "detail" in data:
            return str(data["detail"])

        return str(data)

    if isinstance(data, list):
        return str(data[0])

    return str(data)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        error_code = "API_ERROR"

        if response.status_code == 404:
            error_code = "RESOURCE_NOT_FOUND"

        elif response.status_code == 400:
            error_code = "VALIDATION_ERROR"

        elif response.status_code == 401:
            error_code = "AUTHENTICATION_ERROR"

        elif response.status_code == 403:
            error_code = "PERMISSION_DENIED"

        elif response.status_code == 429:
            error_code = "THROTTLED"

        return Response(
            {
                "success": False,
                "message": get_error_message(response.data),
                "error_code": error_code,
            },
            status=response.status_code,
        )

    return response