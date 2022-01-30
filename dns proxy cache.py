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
        data, addres = _socket.recvfrom(512)
    except:
        data = ''
        addres = ('', 0)
        return data, addres
    return data, addres


def byte_in_bit(_byte):
    tmp = []
    for i in range(8):
        if _byte & (1 << (7 - i)):
            tmp.append(1)
        else:
            tmp.append(0)
    return tmp


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
        dns_not_id_header = args[0][2:]
        _id = args[0][:2]
        key = (name, dns_not_id_header, frozenset(kwargs.items()))
        if key in _cache:
            if _cache[key] is not None:
                print('[*] Received cache DNS %d bytes from localhost' % len(_cache[key]))
                print('[?] Len caches: ', len(_cache))
                return _id + _cache[key]
        result = func(*args, **kwargs)
        if result is not None:
            if dns_ot(result):
                _cache[key] = result[2:]
        return result
    return wrapper


def dns(dns, _DEBUG = False):
    ID = dns[0:2]
    tmp = byte_in_bit(dns[2])
    QR = tmp[0]
    RD = tmp[-1]
    QDCOUNT = dns[4:6]
    ANCOUNT = dns[6:8]
    NSCOUNT = dns[8:10]
    ARCOUNT = dns[10:12]
    if _DEBUG:
        print(dns)
        print('ID sesion ', ID)
        print('QR = ', QR, 'RD = ', RD)
        print('QDCOUNT ', QDCOUNT)
        print('ANCOUNT', ANCOUNT)
        print('NSCOUNT', NSCOUNT)
        print('ARCOUNT', ARCOUNT)
    tmp = byte_in_bit(dns[12])
    if tmp[0] == 0:
        if _DEBUG:
            print('[*]Normal metka')
        len_metka = '0b'
        for i in [2, 3, 4, 5, 6, 7]:
            len_metka += str(tmp[i])
        len_metka = int(len_metka, 2)
        domen = []
        marker = 13 + len_metka
        domen.append(dns[13:marker].decode('utf-8'))
        len_metka = int(dns[marker])
        while True:
            if len_metka != 0:
                marker += 1
                domen.append(dns[marker:marker + len_metka].decode('utf-8'))
                marker += len_metka
                len_metka = int(dns[marker])
            elif len_metka == 0:
                marker += 1
                break
        QTYPE = dns[marker + 1:marker + 2]
        marker += 2
        QCLASS = dns[marker + 1:marker + 2]
        if _DEBUG:
            print(*domen, sep='.')
            if QTYPE:
                print('QTYPE A type')
            elif QTYPE == 15:
                print('QTYPE MX type')
            elif QTYPE == 2:
                print('QTYPE NS type')
            if QCLASS:
                print('QCLASS IN type \n')
            else:
                print('QCLASS unknown type \n')


def dns_ot(dns, _DEBUG = False):
    ID = dns[0:2]
    if _DEBUG:
        print(dns)
        print('ID sesion ', ID)
    tmp = byte_in_bit(dns[2])
    QR = tmp[0]
    RD = tmp[-1]
    TC = tmp[6]
    QDCOUNT = dns[4:6]
    ANCOUNT = dns[6:8]
    NSCOUNT = dns[8:10]
    ARCOUNT = dns[10:12]
    tmp_rcode = byte_in_bit(dns[3])
    RCODE = '0b'
    for i in [4, 5, 6, 7]:
        RCODE += str(tmp_rcode[i])
    RCODE = int(RCODE, 2)
    if RCODE == 0:
        if _DEBUG:
            print('[*] RCODE 0')
    else:
        print('[!] RCODE error')
        return False
    if _DEBUG:
        print('QDCOUNT ', QDCOUNT)
        print('ANCOUNT', ANCOUNT)
        print('NSCOUNT', NSCOUNT)
        print('ARCOUNT', ARCOUNT)
    tmp = byte_in_bit(dns[12])
    if tmp[0] == 0:
        if _DEBUG:
            print('[*]Normal metka')
        len_metka = '0b'
        for i in [2, 3, 4, 5, 6, 7]:
            len_metka += str(tmp[i])
        len_metka = int(len_metka, 2)
        domen = []
        marker = 13 + len_metka
        domen.append(dns[13:marker].decode('utf-8'))
        len_metka = int(dns[marker])
        while True:
            if len_metka != 0:
                marker += 1
                domen.append(dns[marker:marker + len_metka].decode('utf-8'))
                marker += len_metka
                len_metka = int(dns[marker])
            elif len_metka == 0:
                marker += 1
                break
        QTYPE = dns[marker + 1:marker + 2]
        marker += 2
        QCLASS = dns[marker + 1:marker + 2]
        marker += 2
        if _DEBUG:
            print(*domen, sep='.')
            if QTYPE:
                print('QTYPE A type')
            elif QTYPE == 15:
                print('QTYPE MX type')
            elif QTYPE == 2:
                print('QTYPE NS type')
            if QCLASS:
                print('QCLASS IN type')
            else:
                print('QCLASS unknown type')
        tmp = byte_in_bit(dns[marker])
        if tmp[0] == 1:
            if _DEBUG:
                print('Сжатая сылка')
            len_metka = '0b'
            for i in [2, 3, 4, 5, 6, 7]:
                len_metka += str(tmp[i])
            marker += 1
            tmp = byte_in_bit(dns[marker])
            for i in [0, 1, 2, 3, 4, 5, 6, 7]:
                len_metka += str(tmp[i])
            len_metka = int(len_metka, 2)
            tmp_marker = len_metka
            tmp = byte_in_bit(dns[len_metka])
            if tmp[0] == 0:
                len_metka = '0b'
                for i in [2, 3, 4, 5, 6, 7]:
                    len_metka += str(tmp[i])
                len_metka = int(len_metka, 2)
                domen = []
                tmp_marker += 1
                domen.append(dns[tmp_marker:tmp_marker + len_metka].decode('utf-8'))
                tmp_marker = tmp_marker + len_metka
                len_metka = int(dns[tmp_marker])
                while True:
                    if len_metka != 0:
                        tmp_marker += 1
                        domen.append(dns[tmp_marker:tmp_marker + len_metka].decode('utf-8'))
                        tmp_marker += len_metka
                        len_metka = int(dns[tmp_marker])
                    elif len_metka == 0:
                        marker += 1
                        break
                if _DEBUG:
                    print(*domen, sep='.')
                QTYPE = dns[marker + 1:marker + 2]
                marker += 2
                QCLASS = dns[marker + 1:marker + 2]
                marker += 2
                if _DEBUG:
                    if QTYPE:
                        print('QTYPE A type')
                    elif QTYPE == 15:
                        print('QTYPE MX type')
                    elif QTYPE == 2:
                        print('QTYPE NS type')
                    if QCLASS:
                        print('QCLASS IN type')
                    else:
                        print('QCLASS unknown type')
                TTL = dns[marker:marker + 4]
                marker += 4
                if _DEBUG:
                    print('TTL :', TTL)
    if TC == 0:
        return True
    else:
        print('TC :', TC)
        return False


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
                print('Read localhost %d bytes' % len(local_buffer))
                dns(local_buffer, _DEBUG=True)
                dns_ot(remote_buffer, _DEBUG=True)
                _DEBUG = False


server_loop(local_host, local_port)
