from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    ValidationError, AuthenticationFailed, NotAuthenticated,
    PermissionDenied, NotFound, MethodNotAllowed, Throttled
)
from .response import ApiResponse

def unified_exception_handler(exc, context):
    """统一异常处理器"""
    if isinstance(exc, ValidationError):
        return ApiResponse.error(code=4001, message=str(exc.detail), status=400)
    if isinstance(exc, (AuthenticationFailed, NotAuthenticated)):
        msg = getattr(exc, "detail", "认证失败")
        return ApiResponse.error(code=4002, message=str(msg), status=401)
    if isinstance(exc, PermissionDenied):
        return ApiResponse.error(code=4003, message=str(exc.detail), status=403)
    if isinstance(exc, NotFound):
        return ApiResponse.error(code=4004, message=str(exc.detail), status=404)
    if isinstance(exc, MethodNotAllowed):
        return ApiResponse.error(code=4005, message=str(exc.detail), status=405)
    if isinstance(exc, Throttled):
        return ApiResponse.error(code=4006, message=str(exc.detail), status=429)

    response = exception_handler(exc, context)
    if response is not None:
        return response

    return ApiResponse.error(code=5000, message="服务器内部错误", status=500)
