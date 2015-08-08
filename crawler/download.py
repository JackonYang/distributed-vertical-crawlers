# -*- Encoding: utf-8 -*-
import re
import os

from req import request, request_pages, Pagination
from log4f import debug_logger

log = debug_logger('log/download', 'download')


class job_list:
    def __init__(self, filename):
        self.idx_file = filename

    def load(self):
        keys = set()
        with open(self.idx_file, 'r') as fp:
            keys = {line.strip() for line in fp.readlines()}
        return keys


def dl_profile(ids, url_ptn, cache_dir, validate=None, website=''):
    log_str = ''.join(['{}/', str(len(ids)),
                       ' download ', website, ' profile. ', 'ID={}'])
    for i, id in enumerate(ids):
        fn = os.path.join(cache_dir, '{}.html'.format(id))
        if os.path.exists(fn):
            log.warning('{} exists'.format(fn))
            continue
        url = url_ptn.format(id)
        try:
            log.info(log_str.format(i+1, id))
            content = request(url, filename=fn)
            if validate:
                log.info(u'{} saved in {}'.format(validate(content, id), fn))
        except Exception as e:
            log.error(e)


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
