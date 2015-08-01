# -*- Encoding: utf-8 -*-
import socket
from httplib2 import Http

import re

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

def parse_cate():
    with open('cache/food_home.html', 'r') as f:
        content = ','.join(f.readlines())

    cate_prog = re.compile(r'<a .*?href="(http://www.dianping.com/search/category/[\w/]+)".*?>(.*?)</a>', re.DOTALL)
    res = cate_prog.findall(content)
    for url, name in res:
        print name, url
    print len(res)



if __name__ == '__main__':
    # food_home()
    parse_cate()
