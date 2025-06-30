from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError

def custom_exception_handler(exc, context):
    # Call DRF's default exception handler to get the standard error response.
    response = exception_handler(exc, context)

    if isinstance(exc, DjangoValidationError):
        return Response(
            {"detail": exc.message_dict if hasattr(exc, 'message_dict') else str(exc)},
            status=status.HTTP_400_BAD_REQUEST
        )

    # Add additional custom error handling here
    if response is None:
        # For unhandled exceptions, return a custom error message.
        return Response(
            {"error": "Something went wrong. Please try again."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

    return response
