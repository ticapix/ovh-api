
from aiocache import SimpleMemoryCache, MemcachedCache
import socket
from typing import Dict
import os

def DetectCache(cache: Dict) -> Dict:
    cache['cache'] = SimpleMemoryCache
    s = socket.socket()
    s.settimeout(1)   # timeout in seconds
    try:
        mem_port = int(os.getenv('MEMCACHE_PORT', '11211'))
        mem_host = os.getenv('MEMCACHE_HOST', '11211')
        s.connect((mem_host, mem_port))
        cache['cache'] = MemcachedCache
        cache['endpoint'] = mem_host
        cache['port'] = mem_port
    except Exception:
        pass
    return cache
