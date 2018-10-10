from tornado.testing import AsyncHTTPTestCase
from tornado.ioloop import IOLoop
import service.main as service
import yaml

class TestService(AsyncHTTPTestCase):
    def get_app(self):
        return service.make_app()

    def get_new_ioloop(self):
        return IOLoop.current()

class TestServiceApi(TestService):
    def test_wrong_endpoint(self):
        response = self.fetch('/api/endpoint/wrong/path')
        self.assertEqual(response.code, 400)

    def test_wrong_endpoint(self):
        response = self.fetch('/api/{}/wrong/path'.format('ovh-eu'))
        self.assertEqual(response.code, 400)

    def test_all_paths(self):
        response = self.fetch('/api/{}/'.format('ovh-eu'))
        self.assertEqual(response.code, 200)
        res = yaml.load(response.body)
        self.assertTrue('/me' in res['paths'])

    def test_api_me(self):
        response = self.fetch('/api/{}/me'.format('ovh-eu'))
        self.assertEqual(response.code, 200)
        res = yaml.load(response.body)
        # self.assertTrue('/me' in res['paths'])

class TestServiceApp(TestService):
    def test_homepage(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body, b'Hello, world')

