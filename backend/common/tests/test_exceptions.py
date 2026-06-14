from django.test import TestCase
from unittest.mock import Mock
from rest_framework.exceptions import ValidationError, AuthenticationFailed
from common.exceptions import unified_exception_handler

class TestExceptionHandler(TestCase):
    def test_validation_error(self):
        exc = ValidationError({"field": ["错误"]})
        resp = unified_exception_handler(exc, None)
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.data["code"], 4001)

    def test_authentication_failed(self):
        exc = AuthenticationFailed("token无效")
        resp = unified_exception_handler(exc, None)
        self.assertEqual(resp.status_code, 401)
        self.assertEqual(resp.data["code"], 4002)

    def test_unknown_exception(self):
        exc = ValueError("未知错误")
        resp = unified_exception_handler(exc, None)
        self.assertEqual(resp.status_code, 500)
        self.assertEqual(resp.data["code"], 5000)
