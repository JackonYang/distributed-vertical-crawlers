# -*- Encoding: utf-8 -*-
import os
import redis


def visited(path, conn, name, pagination=False, subfix='.html'):
    if pagination:
        key = lambda filename: filename[:filename.find('_')]
    else:
        key = lambda filename: filename[:-5]

    data = {key(fn) for fn in os.listdir(path) if fn.endswith(subfix)}
    conn.sadd('{}:visited'.format(name), *data)


if __name__ == '__main__':

    BASE_DIR = os.path.dirname(__file__)
    shop_review_dir = os.path.join(BASE_DIR, '../dianping/cache/shop_review')
    shop_prof_dir = os.path.join(BASE_DIR, '../dianping/cache/shop_prof')

    conn = {'host': 'localhost',
            'port': 6379,
            'db': 1,
            }

    r = redis.StrictRedis(**conn)
    review_name = 'dp-review'
    shop_name = 'dp-shop'  # shop profile

    visited(shop_review_dir, r, review_name, pagination=True)
    visited(shop_prof_dir, r, shop_name, pagination=False)
