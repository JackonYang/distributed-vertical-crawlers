# -*- Encoding: utf-8 -*-
import re
import socket
from httplib2 import Http

import time
import random

from log4f import debug_logger

log = debug_logger('log/request', 'root.request')
_last_req = None


def delay(bottom=1, top=2):
    global _last_req
    if _last_req is None:
        _last_req = time.time()
        return 0

    delay = max(0,
                _last_req+random.uniform(bottom, top)-time.time())
    time.sleep(delay)
    _last_req = time.time()
    return delay


def wait(f):
    def _wrap_func(*args, **kwargs):
        log.info('...wait {:.2f} sec'.format(delay()))
        return f(*args, **kwargs)
    return _wrap_func


@wait
def request(url, timeout=2, method='GET', filename=None):
    """return None if timeout"""
    h = Http(timeout=timeout)
    try:
        log.debug('request {}'.format(url))
        rsp, content = h.request(url, method)
    except socket.timeout:
        log.warning('timeout while requesting {}'.format(url))
        return None

    if filename:
        with open(filename, 'w') as f:
            f.write(content)
        log.info('{} saved'.format(filename))

    return content


def request_pages(target, page_range=100, filename_ptn=None):
    """request a list of pages

    page_range is a set / list of pages to request.
       if int, [1, page_range] will be generated.
    """
    if isinstance(page_range, int):
        page_range = range(1, page_range+1)

    # request next page until no more items detected
    for page in page_range:
        filename = filename_ptn and filename_ptn.format(page)
        content = request(target.url(page), filename=filename)
        if not target.parse(content, page):
            break

    resend_pages = target.get_resend()
    if resend_pages:
        request_pages(target, resend_pages)


class Pagination:
    def __init__(self, url_ptn, item_ptn, max_failed=5):
        self.url_ptn = url_ptn
        self.item_ptn = item_ptn
        self.max_failed = max_failed
        self.num_resend = 3

        self.data = []
        self.failed_seq = set()

    def url(self, page):
        return self.url_ptn.format(page)

    def parse(self, content, page):
        if content is None:  # Error
            self.failed_seq.add(page)
            return self.go_on()

        items = self.item_ptn.findall(content)
        if not items:
            return False

        self.data.extend(items)
        return True

    def go_on(self):
        return len(self.failed_seq) <= self.max_failed

    def get_resend(self):
        ret = None
        if self.failed_seq and self.go_on() and self.num_resend:
            ret = self.failed_seq.copy()
            self.failed_seq.clear()
            self.num_resend -= 1
        return ret


if __name__ == '__main__':

    review_item_ptn = re.compile(r'<a target="_blank" title="" href="/member/(\d+)">(.+?)</a>')

    shop_id = '16005090'
    review_url_ptn = ''.join([
        'http://www.dianping.com/shop/',
        shop_id,
        '/review_more?pageno={}',
        ])
    target = Pagination(review_url_ptn, review_item_ptn)

    request_pages(target, 10)

    for pid, name in target.data:
        print pid, name
    print len(target.data)
