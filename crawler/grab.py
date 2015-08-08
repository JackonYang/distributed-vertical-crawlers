# -*- Encoding: utf-8 -*-
import re
import os

from req import request, request_pages, Pagination
from log4f import debug_logger

log = debug_logger('log/dianping', 'dianping')


def grab_cate():
    with open('data/cate_url_xian.txt', 'r') as f:
        for i in f.readlines():
            url = i.split()[-1]
            filename = 'cache/category/{}.html'.format('_'.join(url.split('/')[-4:]))
            if not os.path.exists(filename):
                request(url, filename=filename)


def grab_profile(sids, url_ptn, validate, dir='cache/grab_profile', website=''):

    done = {f[:-5] for f in os.listdir(dir)}
    todo = set(sids) - done
    total = len(todo)

    log_str = ''.join([
        '{}/', str(total),
        ' download ', website, ' profile. ',
        'ID={}'])

    for i, sid in enumerate(todo):
        try:
            url = url_ptn.format(sid)
            filename = '{}/{}.html'.format(dir, sid)
            log.info(log_str.format(i+1, sid))
            content = request(url, filename=filename)
            log.info(validate(content, sid))
        except Exception as e:
            log.error(e)


def grab_shop_review(shop_ids, dir='cache/shop_review', max_page=100):
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


def get_files(dir, files_prefix=''):
    for filename in os.listdir(dir):
        if filename.endswith('.html') and filename.startswith(files_prefix):
            with open(os.path.join(dir, filename)) as f:
                yield (filename[:-5], ''.join(f.readlines()))


if __name__ == '__main__':
    dir_shop_profile = 'cache/profile'

    # get shop id set
    sids = set()
    with open('new-shop-id.txt', 'r') as fp:
        sids = {sid.strip() for sid in fp.readlines()}

    from dianping import shop_name
    dianping_url = 'http://www.dianping.com/shop/{}'
    grab_profile(sids, dianping_url, shop_name, website='dianping', dir=dir_shop_profile)
