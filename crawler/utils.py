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

    conn = {'host': 'localhost',
            'port': 6379,
            'db': 1,
            }

    r = redis.StrictRedis(**conn)
    name = 'dp-review'

    visited(shop_review_dir, r, name, pagination=True)
