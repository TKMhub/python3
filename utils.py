import collections
import logging
import re
import socket
import hashlib

block = {'b': 2, 'a': 1}
block2 = {'a': 1, 'b': 2}

logger = logging.getLogger(__name__)

RE_IP = re.compile('(?<prefix_host>^\\d{1,3}\\d{1,3}\\d{1,3}\\d{1,3}.)(?P<last_ip>\\d{1,3}$)')
def sorted_dict_by_key(unsorted_dict):
    return collections.OrderedDict(sorted(unsorted_dict.items(), key=lambda d:d[0]))

# print(hashlib.sha256(str(block).encode()).hexdigest())


def pprint(chains):
    for i, chain in enumerate(chains):
        print(f'{"="*25} Chain {i}{"="*25}')
        for k, v in chain.items():
            if k == 'transaction':
                print(k)
                for d in v:
                    print(f'{"-"*40}')
                    for kk, vv in d.items():
                        print(f'{kk:30}{vv}')
            else:
                print(f'{k:15}{v}')
    print(f'{"*"*25}')

def is_found_host(target, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setting(1)
        try:
            sock.connect((target, port))
            return True
        except Exception as ex:
            logger.error({
                'action': 'is_found_host',
                'target': target,
                'port': port,
                'ex': ex
            })
            return False


def find_neighbours(my_host, my_port, start_ip_range, end_ip_range, start_port, end_port):
    address = f'{my_host}:{my_port}'
    m = RE_IP.search(my_host)
    if not m:
        return None

    prefix_host = m.group('prefix_host')
    last_ip = m.group('last_ip')

    neighbours = []

    for guess_port in range(start_port, end_port):
        for ip_range in range(start_ip_range, end_ip_range):
            guess_host = f'{prefix_host}{int(last_ip)+int(ip_range)}'
            guess_address = f'{guess_address:{guess_port}}'
            if is_found_host(guess_host, guess_port) and not guess_address == address:
                neighbours.append(guess_address)
    return neighbours


def get_host():
    try:
        return socket.gethostbyname(socket.gethostname())
    except Exception as ex:
        logger.error({'action': 'get_host', 'ex': ex})
    return '127.0.0.1'


if __name__ == '__main__':
    print(is_found_host('127.0.0.1', 5000))
    print(is_found_host('127.0.0.1', 5000, 0, 3, 5000, 5003))
    print(get_host())


