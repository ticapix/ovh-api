
import tornado
import tornado.ioloop
from tornado.web import HTTPError
from tornado.httpclient import AsyncHTTPClient
from tornado import gen
import tornado.log
import logging
import json
from aiocache import cached, MemcachedCache
import yaml
from .convert import convert_api_to_oa3
from .cache import DetectCache
import os

# Extracted from https://github.com/ovh/python-ovh/blob/6e9835d205bb322e3357bebdbef3e1f74cb629da/ovh/client.py#L74 
ENDPOINTS = {
    'ovh-eu': 'https://eu.api.ovh.com/1.0',
    'ovh-us': 'https://api.ovhcloud.com/1.0',
    'ovh-ca': 'https://ca.api.ovh.com/1.0',
    'kimsufi-eu': 'https://eu.api.kimsufi.com/1.0',
    'kimsufi-ca': 'https://ca.api.kimsufi.com/1.0',
    'soyoustart-eu': 'https://eu.api.soyoustart.com/1.0',
    'soyoustart-ca': 'https://ca.api.soyoustart.com/1.0',
}

CACHE = {
    'ttl': int(os.getenv('CACHE_TTL', '3600')), # seconds
}

CACHE = DetectCache(CACHE)

# until there is a better officialy mime type here http://www.iana.org/assignments/media-types/media-types.xhtml 
YAML_CONTENT_TYPE='application/x-yaml'


logger = logging.getLogger('tornado.access')
logger.setLevel(logging.INFO)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

@cached(**CACHE)
async def fetch(url: str):
    logger.info('fetching {}'.format(url))
    client = AsyncHTTPClient()
    res = await client.fetch(url)
    if res.code != 200:
        raise HTTPError(500, reason='origin server {} return an error {}'.format(url, res.code))
    return json.loads(res.body)

@cached(**CACHE)
async def convert_to_openapi3(doc):
    return convert_api_to_oa3(doc)

class ApiHandler(tornado.web.RequestHandler):
    async def get(self, endpoint: str, path: str):
        self.set_header('Content-Type', YAML_CONTENT_TYPE)
        if endpoint not in ENDPOINTS.keys():
            raise HTTPError(400, reason='invalid endpoing. Valid endpoints are {}'.format(', '.join(ENDPOINTS.keys())))
        endpoint_url = ENDPOINTS[endpoint]
        endpoint = await fetch(endpoint_url)
        if 'apis' not in endpoint:
            raise HTTPError(500, reason='origin server {} does not return api paths'.format(endpoint_url))
        paths = list(map(lambda x: x['path'], endpoint['apis']))
        path = '/{}'.format(path)
        if path == '/':
            self.write(yaml.dump({
                'paths': paths
            }))
            return
        if path not in paths:
             raise HTTPError(400, reason='unknowed path {}'.format(path))
        api_url = '{}{}.json'.format(endpoint_url, path)
        api_json = await fetch(api_url)
        api_oa3 = await convert_to_openapi3(api_json)
        self.write(yaml.dump(api_oa3))

def make_app(autoreload=False: bool):
    logger.info('Cache config is {}'.format(CACHE))
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/api/([\w-]+)/(.*)", ApiHandler)
    ], autoreload=autoreload)

