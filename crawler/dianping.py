# -*- Encoding: utf-8 -*-
import re
import os

category_prog = re.compile(r'<a .*?href="(http://www.dianping.com/search/category/[\w/]+)".*?>(.*?)</a>', re.DOTALL)


def cache_idx(dir, prefix='', subfix='.html'):
    """build idx of cache files in dir.
    
    return {key-id: abs filename}
    """
    validate = lambda fn: fn.startswith(prefix) and fn.endswith(subfix)
    key = lambda fn: fn[len(prefix): -len(subfix)]

    return {key(fn): os.path.join(dir, fn)
            for fn in os.listdir(dir) if validate(fn)}


def shop_profile(dir):
    files = cache_idx(dir)
    print '{} files exists'.format(len(files))

if __name__ == '__main__':
    dir_shop_profile = 'cache/profile'
    shop_profile(dir_shop_profile)
