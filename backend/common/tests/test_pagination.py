from django.test import TestCase
from common.pagination import StandardPagination

class TestStandardPagination(TestCase):
    def test_default_page_size(self):
        pagination = StandardPagination()
        self.assertEqual(pagination.page_size, 20)
        self.assertEqual(pagination.max_page_size, 100)
        self.assertEqual(pagination.page_query_param, "page")
        self.assertEqual(pagination.page_size_query_param, "page_size")
