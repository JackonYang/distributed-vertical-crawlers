# -*- Encoding: utf-8 -*-
import re
import os

from log4f import debug_logger

log = debug_logger('log/parser', 'parser')

ignore = {
    '15923760': u'商户不存在',
    '21411682': u'没有评分数据',
    '13775000': u'没有评分数据',
    }


def cache_idx(cache_dir, prefix='', subfix='.html'):
    """build idx of cache files in cache_dir.

    return {key-id: filename with abs path}
    """
    validate = lambda fn: fn.startswith(prefix) and fn.endswith(subfix)
    key = lambda fn: fn[len(prefix): -len(subfix)]

    return {key(fn): os.path.join(cache_dir, fn)
            for fn in os.listdir(cache_dir) if validate(fn)}


def parse(progs, content, id, name, log_not_match=True):
    for idx, p in enumerate(progs):
        m = p.findall(content)
        if m:
            if len(m) > 1:
                log.error('multi-match {} {}. prog-idx={}'.format(id, name, idx))
            if isinstance(m[0], str):
                return m[0].decode('utf8')
            else:
                return m[0]

    if log_not_match:
        log.error('failed to match {} {}'.format(id, name))
    return None


def detect(content, ptn):
    return ptn.findall(content)


if __name__ == '__main__':
    dir_shop_profile = 'cache/profile'
    cache_files = cache_idx(dir_shop_profile)
    print '{} files exists'.format(len(cache_files))
