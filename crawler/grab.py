# -*- Encoding: utf-8 -*-
import re
import os

from db import job_shop_review
from db import add_one, exists

from utils import request, request_pages, Pagination


def grab_cate():
    with open('data/cate_url_xian.txt', 'r') as f:
        for i in f.readlines():
            url = i.split()[-1]
            filename = 'cache/category/{}.html'.format('_'.join(url.split('/')[-4:]))
            if not os.path.exists(filename):
                request(url, filename=filename)


def grab_shops(shop_ids, dir='cache/shops'):
    for sid in shop_ids:
        url = 'http://www.dianping.com/shop/{}'.format(sid)
        filename = '{}/{}.html'.format(dir, sid)
        if not os.path.exists(filename):
            request(url, filename=filename)


def grab_shop_review(shop_ids, dir='cache/shop_review'):
    review_item_ptn = re.compile(r'<a target="_blank" title="" href="/member/(\d+)">(.+?)</a>')
    for sid in shop_ids:
        if not exists(job_shop_review, sid=sid):
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
            request_pages(target, 9, filename_ptn=filename)
            print '--got {} reviews'.format(len(target.data))
            add_one(job_shop_review,
                       shop_id=sid, num=len(target.data))
        else:
            print '{} exists'.format(sid)


if __name__ == '__main__':
    sids = []
    with open('data/shops.txt', 'r') as f:
        sids = [sid.strip() for sid in f.readlines()]

    grab_shops(sids)
    grab_shop_review(sids)
