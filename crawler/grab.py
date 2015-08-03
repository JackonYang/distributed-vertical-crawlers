# -*- Encoding: utf-8 -*-
import re
import os

from db import job_shop_review, shop_profile
from db import add_one, exists
import parser

from req import request, request_pages, Pagination


def grab_cate():
    with open('data/cate_url_xian.txt', 'r') as f:
        for i in f.readlines():
            url = i.split()[-1]
            filename = 'cache/category/{}.html'.format('_'.join(url.split('/')[-4:]))
            if not os.path.exists(filename):
                request(url, filename=filename)


def grab_shop_profile(sids, dir='cache/shops'):
    for sid in sids:
        url = 'http://www.dianping.com/shop/{}'.format(sid)
        filename = '{}/{}.html'.format(dir, sid)
        if not os.path.exists(filename):
            print 'grab_shop. {}'.format(sid)
            try:
                content = request(url, filename=filename)

                name = parser.parse_shop_name(content)
                star = parser.parse_shop_star(content)

                add_one(shop_profile, sid=sid, shop_name=name, star=star)
                print u'-- {} - {} saved in db'.format(name, star/10.0)
            except Exception as e:
                print e


def grab_shop_review(shop_ids, dir='cache/shop_review'):
    review_item_ptn = re.compile(r'href="/member/(\d+)">(.+?)</a>')
    review_url_ptn = ('http://www.dianping.com/shop/{id}'
                      '/review_more?pageno={page}')

    for sid in shop_ids:
        if not exists(job_shop_review, sid=sid):
            target = Pagination(review_item_ptn, review_url_ptn,
                                sid, id_name='shop_ID')

            filename = ''.join([dir, '/review_', sid, '_{page}.html'])
            print 'request reviews of shop {}'.format(sid)
            request_pages(target, 9, filename_ptn=filename)
            print '--got {} reviews'.format(len(target.data))
            add_one(job_shop_review, sid=sid, num=len(target.data))
        else:
            print '{} exists'.format(sid)


if __name__ == '__main__':
    sids = []
    with open('data/shops.txt', 'r') as f:
        sids = [sid.strip() for sid in f.readlines()]

    grab_shop_profile(sids)
    grab_shop_review(sids)
