# -*- Encoding: utf-8 -*-
import socket
from httplib2 import Http


def request(url, timeout=2, method='GET'):
    """return None if timeout"""
    h = Http(timeout=timeout)
    try:
        rsp, content = h.request(url, method)
    except socket.timeout:
        return None
    return content


def food_home(url='http://www.dianping.com/xian/food'):
    content = request(url)

    with open('cache/food_home.html', 'w') as f:
        f.write(content)


if __name__ == '__main__':
    food_home()
