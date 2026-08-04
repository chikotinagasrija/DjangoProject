from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['GET'])
def welcome_api(request):
    data = {
        "message": "Welcome to my first API",
        "status": "success"
    }
    return Response(data)
