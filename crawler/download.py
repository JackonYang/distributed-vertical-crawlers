# -*- Encoding: utf-8 -*-
"""builk requests for some kinds of web pages
"""
import re
import os

from req import request, request_pages

from log4f import debug_logger

log = debug_logger('log/download', 'download')


class RecursiveJob:
    def __init__(self, ptn, table, session):
        self.table = table  # subclass of Peer in model.py
        self.session = session

        self.ptn = ptn

    def build_idx(self, path, parse_key):
        # full scan of a path
        print 'begin to build idx of files in {}'.format(path)
        for fn in os.listdir(path):
            key = parse_key(fn)
            if key:
                with open(os.path.join(path, fn)) as f:
                    self.feed(''.join(f.readlines()), key)
        self.session.commit()
        print 'end of build idx of files in {}'.format(path)

    def get_todo(self):
        get = lambda col:\
            {i[0] for i in self.session.query(col).distinct().all()}
        return get(self.table.key2) - get(self.table.key1)

    def feed(self, content, key, auto_commit=True):
        data = set(self.ptn.findall(content))
        self.session.add_all([self.table(key, i) for i in data])
        if auto_commit:
            self.session.commit()
        return '{} items'.format(len(data))


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
                log.info(u'{} found. saved in {}'.format(
                    validate(content, key), fn)
                    )
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
