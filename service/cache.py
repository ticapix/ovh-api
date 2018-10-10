
from aiocache import SimpleMemoryCache, MemcachedCache
import socket
import os

def DetectCache(cache: dict) -> dict:
    cache['cache'] = SimpleMemoryCache
    mem_port = int(os.getenv('MEMCACHE_PORT', '11211'))
    mem_host = os.getenv('MEMCACHE_HOST', '127.0.0.1')
    try:
        conn = socket.create_connection((mem_host, mem_port), timeout=1)
        print(conn)
        cache['cache'] = MemcachedCache
        cache['endpoint'] = mem_host
        cache['port'] = mem_port
    except Exception:
        pass
    return cache
