
from aiocache import SimpleMemoryCache, MemcachedCache
import socket

def DetectCache():
    s = socket.socket()
    s.settimeout(1)   # timeout in seconds
    try:
        s.connect(('127.0.0.1', 11211))
        return MemcachedCache
    except Exception as e:
        pass
    return SimpleMemoryCache
