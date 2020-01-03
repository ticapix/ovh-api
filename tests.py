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
    def test_wrong_region(self):
        response = self.fetch('/endpoint/wrong/path')
        self.assertEqual(response.code, 400)

    def test_wrong_endpoint(self):
        response = self.fetch('/{}/wrong/path'.format('ovh-eu'))
        self.assertEqual(response.code, 400)

    def test_all_paths(self):
        response = self.fetch('/{}/'.format('ovh-eu'))
        self.assertEqual(response.code, 200)
        res = yaml.load(response.body, Loader=yaml.SafeLoader)
        self.assertTrue('/me' in res['paths'])

    def test_api_me(self):
        response = self.fetch('/{}/me'.format('ovh-eu'))
        self.assertEqual(response.code, 200)
        res = yaml.load(response.body, Loader=yaml.SafeLoader)
        self.assertTrue('/me/api/application' in res['paths'])


class TestServiceApp(TestService):
    def test_homepage(self):
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
