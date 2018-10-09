
from tornado.testing import AsyncHTTPTestCase, main
import unittest
import json
import service.main as service
import yaml

class TestServiceApp(AsyncHTTPTestCase):
    def get_app(self):
        return service.make_app()

    def test_wrong_endpoint(self):
        response = self.fetch('/api/endpoint/wrong/path')
        self.assertEqual(response.code, 400)

    def test_wrong_endpoint(self):
        response = self.fetch('/api/{}/wrong/path'.format(list(service.ENDPOINTS)[0]))
        self.assertEqual(response.code, 400)

    def test_all_paths(self):
        response = self.fetch('/api/{}/'.format(list(service.ENDPOINTS)[0]))
        self.assertEqual(response.code, 200)
        res = yaml.load(response.body)
        self.assertTrue('/me' in res['paths'])

    def test_api_me(self):
        response = self.fetch('/api/{}/me'.format(list(service.ENDPOINTS)[0]))
        self.assertEqual(response.code, 200)
        res = yaml.load(response.body)
        # self.assertTrue('/me' in res['paths'])


    def test_homepage(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, b'Hello, world')

if __name__ == '__main__':
    unittest.main()