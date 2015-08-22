# -*- Encoding: utf-8 -*-
"""builk requests for some kinds of web pages

"""
import re
import os
import shutil
import redis

from req import request, request_pages
from log4f import debug_logger

log = debug_logger('log/download', 'download')


def get_title(content):
    """demo validator of builk_single"""
    m = re.compile(r'<title>(.*?)</title>').search(content)
    if m is None:
        return 'No Title'
    else:
        return m.group(1)


def builk_single(job, url_ptn, cache_dir, find_new=None):
    """builk download. one single corresponding page for one ID.

    usually, it is used for profile page of a user/book/shop etc.
    """
    key = job.next()
    print 'downloading...'
    while key:
        log.info('download {}'.format(key))
        url = url_ptn.format(key)
        fn = os.path.join(cache_dir, '{}.html'.format(key))
        try:
            c = request(url, filename=fn)
            log.info('{} saved in {}'.format(get_title(c), fn))
            if find_new:
                for item in find_new.findall(c):
                    job.add(item)
        except Exception as e:
            log.error('{}. ID={}'.format(e, key))
            job.add(key, force=True)
        key = job.next()


def builk_pages(job, url_ptn, cache_dir, find_item, recursive=False,
                min_num=0, max_page=100, page_start=0):
    filename_ptn = os.path.join(cache_dir, '{}_{}.html')
    key = job.next()
    while key:
        log.info('downloading {}'.format(key))
        try:
            ret = request_pages(key, range(page_start, max_page),
                                url_ptn, find_item,
                                min_num=min_num,
                                filename_ptn=filename_ptn)
            log.info('{} items in {}'.format(len(ret), key))
            if recursive:
                for item in ret:
                    job.add(item)
        except Exception as e:
            log.error('{}. ID={}'.format(e, key))
            job.add(key, force=True)
        key = job.next()


def init_test_path():
    path = 'test_data'
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
    return path


if __name__ == '__main__':
    from job import JobPool

    cache_root = 'test_data'

    r = redis.StrictRedis()
    r.flushall()
    j = JobPool(r, cache_root, 'single', pagination=False)

    seed = ['22124523', '5195730']
    job.init_db(seed)

    url_pages = 'http://www.dianping.com/shop/{key}/review_more?pageno={page}'
    rev_ptn = re.compile(r'href="/member/(\d+)">(.+?)</a>')
    find_rev = lambda c, key: rev_ptn.findall(c)

    init_test_path()
    builk_pages(job, url_pages, path, find_item=find_rev, recursive=False)

    job.add('22124523')
    job.add('5195730')

    url_single = 'http://www.dianping.com/shop/{}'
    sid_ptn = re.compile(r'href="/shop/(\d+)(?:\?[^"]+)?"')
    builk_single(job, url_single, path, find_new=sid_ptn)
