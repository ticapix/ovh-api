
from aiocache import SimpleMemoryCache, MemcachedCache
import socket
import os


def DetectCache(cache: dict) -> dict:
    cache['cache'] = SimpleMemoryCache
    mem_port = int(os.getenv('MEMCACHED_PORT', '11211'))
    mem_host = os.getenv('MEMCACHED_HOST', '127.0.0.1')
    try:
        _ = socket.create_connection((mem_host, mem_port), timeout=1)
        cache['cache'] = MemcachedCache
        cache['endpoint'] = mem_host
        cache['port'] = mem_port
    except Exception:
        pass
    return cache
