# -*- Encoding: utf-8 -*-
import socket
from httplib2 import Http
import re

import os

import time
import random

import db
from utils import request_pages, Pagination


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


def grab_cate():
    with open('data/cate_url_xian.txt', 'r') as f:
        for i in f.readlines():
            url = i.split()[-1]
            filename = 'cache/category/{}.html'.format('_'.join(url.split('/')[-4:]))
            if not os.path.exists(filename):
                print 'request: {}'.format(url)
                request(url, filename=filename)
                print '{} saved'.format(filename)


def grab_shops(shop_ids, dir='cache/shops'):
    for sid in shop_ids:
        url = 'http://www.dianping.com/shop/{}'.format(sid)
        filename = '{}/{}.html'.format(dir, sid)
        if not os.path.exists(filename):
            print 'request: {}'.format(url)
            request(url, filename=filename)
            print '{} saved'.format(filename)


def grab_shop_review(shop_ids, dir='cache/shop_review'):
    review_item_ptn = re.compile(r'<a target="_blank" title="" href="/member/(\d+)">(.+?)</a>')
    for sid in shop_ids:
        if not db.shop_review_exists(sid):
            review_url_ptn = ''.join([
                'http://www.dianping.com/shop/',
                sid,
                '/review_more?pageno={}',
                ])

            target = Pagination(review_url_ptn, review_item_ptn)
            filename = ''.join([
                dir,
                '/review_',
                sid,
                '_{}.html',
                ])
            print 'request reviews of shop {}'.format(sid)
            request_pages(target, 9, filename=filename)
            print 'got {} reviews'.format(len(target.data))
            db.add_one(db.his_shop_review,
                       shop_id=sid, num=len(target.data), run_info='success')
        else:
            print '{} exists'.format(sid)


if __name__ == '__main__':
    sids = []
    with open('data/shops.txt', 'r') as f:
        sids = [sid.strip() for sid in f.readlines()]
    # grab_shops(sids)
    grab_shop_review(sids)
