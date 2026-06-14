from django.test import TestCase
from common.response import ApiResponse

class TestApiResponse(TestCase):
    def test_success_format(self):
        resp = ApiResponse.success(data={"key": "value"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data, {"code": 0, "data": {"key": "value"}, "message": "ok"})

    def test_error_format(self):
        resp = ApiResponse.error(code=4001, message="参数错误")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data, {"code": 4001, "data": None, "message": "参数错误"})

    def test_custom_status_code(self):
        resp = ApiResponse.error(code=5000, message="内部错误", status=500)
        self.assertEqual(resp.status_code, 500)
