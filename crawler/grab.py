# -*- Encoding: utf-8 -*-
import socket
from httplib2 import Http

import os

import time
import random


_last_req = None
def delay():
    global _last_req

    if _last_req is None:
        _last_req = time.time()
        return

    next_req = _last_req + random.uniform(2, 10)  # wait 2-10s, avg: 6s
    now = time.time()
    if next_req > now:
        time.sleep(next_req-now)
    else:
        print 'next_req<now, {}'.format(next_req-_last_req)
    _last_req = next_req


def wait(f):
    def _wrap_func(*args, **kwargs):
        delay()
        return f(*args, **kwargs)
    return _wrap_func


@wait
def request(url, timeout=2, method='GET', filename=None):
    """return None if timeout"""
    h = Http(timeout=timeout)
    try:
        rsp, content = h.request(url, method)
    except socket.timeout:
        return None

    if filename:
        with open(filename, 'w') as f:
            f.write(content)

    return content


if __name__ == '__main__':
    with open('data/cate_url_xian.txt', 'r') as f:
        for i in f.readlines():
            url = i.split()[-1]
            filename = 'cache/{}.html'.format('_'.join(url.split('/')[-4:]))
            if not os.path.exists(filename):
                print 'request: {}'.format(url)
                request(url, filename=filename)
                print '{} saved'.format(filename)
