# -*- Encoding: utf-8 -*-
"""builk requests for some kinds of web pages
"""
import re
import os

from req import request, request_pages, Pagination
from log4f import debug_logger

log = debug_logger('log/download', 'download')


def get_title(content, key):
    """demo validator of builk_single"""
    m = re.compile(r'<title>(.*?)</title>').findall(content)
    if not m:
        return 'No Title'
    return m[0].decode('utf8')


def builk_single(ids, url_ptn, cache_dir, validate=get_title, page_name=''):
    """builk download. one single corresponding page for one ID.

    usually, it is used for profile page of a user/book/shop etc.
    """
    log_str = ''.join(['{}/', str(len(ids)),
                       ' download ', page_name, '. ID={}'])
    fails = set()
    for i, key in enumerate(ids):
        fn = os.path.join(cache_dir, '{}.html'.format(key))
        if os.path.exists(fn):
            log.info('{} existed. ID={}'.format(page_name, key))
            continue
        url = url_ptn.format(key)
        try:
            log.info(log_str.format(i+1, key))
            content = request(url, filename=fn)
            if validate:
                log.info(u'{} found. saved in {}'.format(validate(content, key), fn))
        except Exception as e:
            fails.add(key)
            log.error('{}. ID={}'.format(e, key))
    return fails


def dl_shop_review(shop_ids, dir='cache/shop_review', max_page=100):
    review_item_ptn = re.compile(r'href="/member/(\d+)">(.+?)</a>')
    review_url_ptn = ('http://www.dianping.com/shop/{id}'
                      '/review_more?pageno={page}')

    for sid in shop_ids:
        target = Pagination(review_item_ptn, review_url_ptn,
                            sid, id_name='shop_ID')

        filename = ''.join([dir, '/review_', sid, '_{page}.html'])
        log.info('download reviews. shop ID={}'.format(sid))
        request_pages(target, max_page, filename_ptn=filename)
        log.info('number of reviews: {}'.format(len(target.data)))


def empty_path(path):
    if os.path.exists(path):
        import shutil
        shutil.rmtree(path)
    os.makedirs(path)


if __name__ == '__main__':
    testdir_pf = 'test_data/dl_pf'

    empty_path(testdir_pf)  # empty path for test

    keys = ['22949597', '24768319', '22124523']
    url_pf = 'http://www.dianping.com/shop/{}'
    builk_single(keys, url_pf, testdir_pf, page_name='dianping shop profile')
    builk_single(keys, url_pf, testdir_pf, validate=get_title, page_name='dianping shop profile')
