# -*- Encoding: utf-8 -*-
import re
import socket
from httplib2 import Http

import time
import random

from log4f import debug_logger

log = debug_logger('log/request', 'root.request')
_last_req = None


def delay(bottom=2, top=7):
    global _last_req
    if _last_req is None:
        _last_req = time.time()
        return 0

    period = max(0,
                 _last_req+random.uniform(bottom, top)-time.time())
    log.debug('...wait {:.2f} sec'.format(period))
    time.sleep(period)
    _last_req = time.time()
    return period


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
        log.debug('request {}'.format(url))
        rsp, content = h.request(url, method)
    except socket.timeout:
        return None

    if filename:
        with open(filename, 'w') as f:
            f.write(content)
        log.debug('response saved. filename={}'.format(filename))

    return content


def request_pages(key, page_range, url_ptn, item_ptn, resend=3,
                  min_num=0, max_failed=5, filename_ptn=None):
    """request a list of pages in page_range

    """
    items_total = set()  # items will be out of order if some pages failed
    failed = set()

    for page in page_range:

        filename = filename_ptn and filename_ptn.format(key=key, page=page)
        page_url = url_ptn.format(key=key, page=page)
        content = request(page_url, filename=filename)

        if content is not None:
            items_page = item_ptn.findall(content)
            if items_page and len(items_page) > min_num:
                items_total.update(items_page)
            else:
                log.debug('nothing in page {} of {}'.format(page, key))
                break
        else:
            log.warning('failed to request page {} of {}'.format(page, key))
            failed.add(page)
            if len(failed) > max_failed:
                log.error('more timeout than {}'.format(max_failed))
                return

    if failed:
        if not resend:
            return None
        log.debug('resend failed pages of {}'.format(key))
        items_more = request_pages(key, failed, url_ptn, item_ptn,
                                   resend-1, min_num, filename_ptn)
        if items_more is None:
            return None
        items_total.update(items_more)
    return items_total


if __name__ == '__main__':

    url = 'http://www.dianping.com/shop/{key}/review_more?pageno={page}'
    item_ptn = re.compile(r'href="/member/(\d+)">(.+?)</a>')
    uid = '5195730'  # 45 reviews on 2015.8.3
    pages = range(1, 9)

    ret = request_pages(uid, pages, url, item_ptn, resend=3,
                        min_num=0, max_failed=5, filename_ptn=None)
    for user, name in ret:
        print user, name
    print len(ret)
