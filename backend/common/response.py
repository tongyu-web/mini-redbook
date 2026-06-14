from rest_framework.response import Response

class ApiResponse:
    """统一响应格式: {"code": 0, "data": ..., "message": "ok"}"""

    @staticmethod
    def success(data=None, message="ok", status=200):
        return Response({
            "code": 0,
            "data": data,
            "message": message
        }, status=status)

    @staticmethod
    def error(code=4001, message="error", data=None, status=400):
        return Response({
            "code": code,
            "data": data,
            "message": message
        }, status=status)
