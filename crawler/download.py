# -*- Encoding: utf-8 -*-
import re
import os

from req import request, request_pages, Pagination
from log4f import debug_logger

log = debug_logger('log/download', 'download')


class job_list:
    def __init__(self, filename, action):
        self.idx_file = filename
        if not os.path.exists(self.idx_file):
            self.dump(action())

    def load(self):
        keys = set()
        with open(self.idx_file, 'r') as fp:
            keys = {line.strip() for line in fp.readlines()}
        return keys

    def dump(self, data):
        with open(self.idx_file, 'w') as fw:
            fw.write('\n'.join(data))


def dl_profile(keys, url_ptn, cache_dir, validate=None, page_name=''):
    log_str = ''.join(['{}/', str(len(keys)),
                       ' download ', page_name, ' profile. ', 'ID={}'])
    fails = set()
    for i, key in enumerate(keys):
        fn = os.path.join(cache_dir, '{}.html'.format(key))
        if os.path.exists(fn):
            log.info('{} exists'.format(fn))
            continue
        url = url_ptn.format(key)
        try:
            log.info(log_str.format(i+1, key))
            content = request(url, filename=fn)
            if validate:
                log.info(u'{} saved in {}'.format(validate(content, key), fn))
        except Exception as e:
            fails.add(key)
            log.error(e)
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


if __name__ == '__main__':
    keys = ['22949597', '24768319', '22124523']

    # -------------- test profile -------------------
    url_pf = 'http://www.dianping.com/shop/{}'
    dir_pf = 'test_dl/pf'

    def get_title(content, key):
        m = re.compile(r'<title>(.*?)</title>').findall(content)
        if m:
            return m[0].decode('utf8')
        else:
            return 'no title matched'

    if os.path.exists(dir_pf):
        import shutil
        shutil.rmtree(dir_pf)
    os.makedirs(dir_pf)


    dl_profile(keys, url_pf, dir_pf, validate=get_title, page_name='dianping shop')
    dl_profile(keys, url_pf, dir_pf, validate=get_title, page_name='dianping shop')
