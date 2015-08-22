# -*- Encoding: utf-8 -*-
import re
import os
import redis

import sys
parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent)

from argparse import ArgumentParser
from crawler.download import builk_single, builk_pages
from crawler.job import JobPool


# config
BASE_DIR = os.path.dirname(__file__)
shop_prof_dir = os.path.join(BASE_DIR, 'cache/shop_prof')
user_prof_dir = os.path.join(BASE_DIR, 'cache/user_prof')
shop_review_dir = os.path.join(BASE_DIR, 'cache/shop_review')
shop_review_idx = os.path.join(BASE_DIR, 'cache/index/review-id.json')

cache_root = 'cache'

for path in [shop_prof_dir, shop_review_dir, user_prof_dir]:
    if not os.path.exists(path):
        os.makedirs(path)

# const
sid_ptn = re.compile(r'href="/shop/(\d+)(?:\?[^"]+)?"')
rev_ptn = re.compile(r'<li[^>]+id="rev_(\d+)"')
uid_ptn = re.compile(r'href="/member/(\d+)(?:\?[^"]+)?"')

find_rev = lambda c, key: set(rev_ptn.findall(c))


def grab_shop_prof(conn_redis):
    job_name = 'shop_prof'
    job = JobPool(conn_redis, cache_root, job_name, pagination=False)

    find_job = lambda data: {v for vs in data.values() for v in vs}
    job.scan(shop_prof_dir, sid_ptn, find_job)

    url = 'http://www.dianping.com/shop/{}'

    print 'grabbing shop prof. total: {}'.format(job.count())
    builk_single(job, url, shop_prof_dir, find_new=sid_ptn)


def grab_user_prof(conn_redis):
    job_name = 'user_prof'
    job = JobPool(conn_redis, cache_root, job_name, pagination=False)

    find_job = lambda data: {v for vs in data.values() for v in vs}
    job.scan(shop_review_dir, uid_ptn, find_job)

    url = 'http://www.dianping.com/member/{}'

    print 'grabbing shop prof. total: {}'.format(job.count())
    builk_single(job, url, user_prof_dir, find_new=uid_ptn)


def grab_shop_reviews(conn_redis, threshold=10):
    job_name = 'shop_review'
    job = JobPool(conn_redis, cache_root, job_name, pagination=True)

    find_job = lambda data: {key[:-5] for key, vs in data.items()
                             if len(vs) > 9}
    job.scan(shop_prof_dir, rev_ptn, find_job)

    url = 'http://www.dianping.com/shop/{key}/review_more?pageno={page}'

    print 'grabbing shop reviews... TODO: {}'.format(job.count())
    builk_pages(job, url, shop_review_dir, find_item=find_rev,
                page_start=1, recursive=False)


if __name__ == '__main__':
    r = redis.StrictRedis()

    args_parser = ArgumentParser(
        description='Data Bang-Distributed Vertical Crawler')
    args_parser.add_argument('page', type=str,
                             help='page type',
                             choices=['profile', 'reviews', 'user_prof'])
    args_parser.add_argument('--rebuild', action='store_true',
                             default=False)  # rebuild index

    args = args_parser.parse_args()

    page_type = args.page
    rebuild_idx = args.rebuild

    if page_type == 'profile':
        grab_shop_prof(r)
    elif page_type == 'reviews':
        grab_shop_reviews(r)
    elif page_type == 'user_prof':
        grab_user_prof(r)
