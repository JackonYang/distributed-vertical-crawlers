# -*- Encoding: utf-8 -*-
import os
import re
import redis


def visited(path, conn, name, pagination=False, subfix='.html'):
    if pagination:
        key = lambda filename: filename[:filename.find('_')]
    else:
        key = lambda filename: filename[:-5]

    data = {key(fn) for fn in os.listdir(path) if fn.endswith(subfix)}
    conn.sadd('{}:visited'.format(name), *data)


def find_todo(path, conn, name, ptn, func=None):

    if func is None:
        func = lambda ptn, c, filename: set(ptn.findall(c))

    visited = conn.smembers('{}:visited'.format(name))
    print len(visited)

    cache = set()

    for i, fn in enumerate(os.listdir(path)):
        if i % 5000 == 0:
            todo = cache - visited
            if todo:
                conn.lpush('{}:todo'.format(name), *todo)
            cache.clear()
            print i, len(todo)
        with open(os.path.join(path, fn), 'r') as f:
            cache.update(func(ptn, ''.join(f.readlines()), filename=fn))


if __name__ == '__main__':

    BASE_DIR = os.path.dirname(__file__)
    shop_review_dir = os.path.join(BASE_DIR, '../dianping/cache/shop_review')
    shop_prof_dir = os.path.join(BASE_DIR, '../dianping/cache/shop_prof')
    user_prof_dir = os.path.join(BASE_DIR, '../dianping/cache/user_prof')

    conf = {'host': 'localhost',
            'port': 6379,
            'db': 1,
            }

    r = redis.StrictRedis(**conf)
    review_name = 'dp-review'
    shop_name = 'dp-shop'  # shop profile
    user_name = 'dp-user'  # user-profile

    visited(shop_review_dir, r, review_name, pagination=True)
    visited(shop_prof_dir, r, shop_name, pagination=False)

    rev_ptn = re.compile(r'<li[^>]+id="rev_(\d+)"')
    sid_ptn = re.compile(r'href="/shop/(\d+)(?:\?[^"]+)?"')
    uid_ptn = re.compile(r'href="/member/(\d+)(?:\?[^"]+)?"')

    def rev_func(ptn, c, filename):
        if len(ptn.findall(c)) > 9:
            return {filename[:-5]}

        return set()

    find_todo(shop_prof_dir, r, review_name, rev_ptn, func=rev_func)
    find_todo(shop_prof_dir, r, shop_name, sid_ptn)
    find_todo(shop_prof_dir, r, user_name, sid_ptn)
