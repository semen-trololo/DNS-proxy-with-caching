import socket

local_host = '127.0.0.1'
local_port = 53
remote_host = '192.168.0.1'
remote_port = 53
_cache = {}
_DEBUG = True


def receive_from(_socket):
    _socket.settimeout(1)
    try:
        data, addres = _socket.recvfrom(4096)
    except:
        data = ''
        addres = ('', 0)
        return data, addres
    return data, addres


def dns_receive_remore(local_buffer, local_addr, remote_socket):

    if len(local_buffer) and len(local_addr[0]):
        try:
            remote_socket.sendto(local_buffer, (remote_host, remote_port))
        except:
            print('[!]Can not send DNS to remote.')
        remote_buffer, remore_addr = receive_from(remote_socket)
        if len(remote_buffer):
            return remote_buffer
    return None


def memoize(func):
    """ Декоратов для обработки кеша запроса функции."""
    def wrapper(*args, **kwargs):
        name = func.__name__
        key = (name, args[0], frozenset(kwargs.items()))
        if key in _cache:
            if _cache[key] is not None:
                print('[*] Received cache DNS %d bytes from localhost' % len(_cache[key]))
            return _cache[key]
        result = func(*args, **kwargs)
        if result is not None:
            _cache[key] = result
        return result
    return wrapper


def server_loop(local_host, local_port):
    global _DEBUG
    server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        server.bind((local_host, local_port))
    except:
        print("[!!] Failed to listen on %s:%d" % (local_host, local_port))
        print("[!!] Check for other listening sockets or correct permissions.")
    print("[*] Listening on %s:%d" % (local_host, local_port))
    remote_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    cache = memoize(dns_receive_remore)
    while True:
        local_buffer, local_addr = receive_from(server)
        remote_buffer = cache(local_buffer, local_addr, remote_socket)
        if remote_buffer is not None:
            server.sendto(remote_buffer, local_addr)
            if _DEBUG:
                print('Send localhost %d bytes' % len(remote_buffer))
                _DEBUG = False


server_loop(local_host, local_port)
