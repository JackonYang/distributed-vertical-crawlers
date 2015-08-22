# -*- Encoding: utf-8 -*-
import re
import os
import redis

import sys
parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent)

from argparse import ArgumentParser
from crawler.download import builk_single, builk_pages
from crawler.model import install, Peer, HisCount
from crawler.job import JobPool


# config
BASE_DIR = os.path.dirname(__file__)
shop_prof_dir = os.path.join(BASE_DIR, 'cache/shop_prof')
shop_review_dir = os.path.join(BASE_DIR, 'cache/shop_review')
shop_review_idx = os.path.join(BASE_DIR, 'cache/index/review-id.json')

for path in [shop_prof_dir, shop_review_dir]:
    if not os.path.exists(path):
        os.makedirs(path)

# const
sid_ptn = re.compile(r'href="/shop/(\d+)(?:\?[^"]+)?"')
rev_ptn = re.compile(r'<li[^>]+id="rev_(\d+)"')
uid_ptn = re.compile(r'href="/member/(\d+)(?:\?[^"]+)?"')

rev_name = 'dp-reviews'
find_rev = lambda c, key: set(rev_ptn.findall(c))


class ShopProfPeer(Peer):
    __tablename__ = 'ShopProfPeer'


def init_shop_prof_job(session):
    fn_key = lambda fn: fn.endswith('.html') and fn[:-5]

    jobs = RecursiveJob(sid_ptn, ShopProfPeer, session)
    jobs.build_idx(shop_prof_dir, fn_key)


def grab_shop_prof(session):
    page_name = 'DianPing Shop Profile'
    url = 'http://www.dianping.com/shop/{}'
    jobs = RecursiveJob(sid_ptn, ShopProfPeer, session)

    todo = jobs.get_todo()
    if not todo:
        init_shop_prof_job(session)
        todo = jobs.get_todo()

    while todo:
        print 'grabbing shop prof. total: {}'.format(len(todo))
        builk_single(todo, url, shop_prof_dir, jobs.feed, page_name)
        todo = jobs.get_todo()
    else:
        print 'no shop id found'


# uid and reviews


class ShopReviewCnt(HisCount):
    __tablename__ = 'Shop_review_cnt'


def grab_shop_reviews(conn_redis, threshold=10):

    cache_root = 'cache'
    job_name = 'shop_review'
    job = JobPool(conn_redis, cache_root, job_name, pagination=True)

    job.scan(shop_prof_dir, rev_ptn)
    total = {key[:-5] for key, vs in job.data.items() if len(vs) > 9}
    job.init_db(total)

    url = 'http://www.dianping.com/shop/{key}/review_more?pageno={page}'

    print 'grabbing shop reviews... TODO: {}'.format(job.count())
    key = job.next()
    while key:
        builk_pages(job, url, shop_review_dir, find_item=find_rev,
                    page_start=1, recursive=False)
        key = job.next()
    else:
        print 'no more jobs'


if __name__ == '__main__':
    db_pf = 'sqlite:///cache/db_profile.sqlite3'
    Session = install(db_pf)
    session = Session()

    r = redis.StrictRedis()
    r.flushall()

    args_parser = ArgumentParser(
        description='Data Bang-Distributed Vertical Crawler')
    args_parser.add_argument('page', type=str,
                             help='page type',
                             choices=['profile', 'reviews'])
    args_parser.add_argument('--rebuild', action='store_true',
                             default=False)  # rebuild index

    args = args_parser.parse_args()

    page_type = args.page
    rebuild_idx = args.rebuild

    if page_type == 'profile':
        if rebuild_idx:
            init_shop_prof_job(session)
        grab_shop_prof(session)
    elif page_type == 'reviews':
        grab_shop_reviews(r)

    session.close()
