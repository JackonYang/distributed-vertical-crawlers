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


def cache_idx(cache_dir, idx_file=None, prefix='', subfix='.html'):
    """build idx of cache files in cache_dir.

    return {key-id: filename with abs path}
    """
    validate = lambda fn: fn.startswith(prefix) and fn.endswith(subfix)
    key = lambda fn: fn[len(prefix): -len(subfix)]

    idx = {key(fn): os.path.join(cache_dir, fn)
           for fn in os.listdir(cache_dir) if validate(fn)}
    if idx_file:
        with open(idx_file, 'w') as fp:
            fp.write('\n'.join(['{},{}'.format(k, v) for k, v in idx.items()]))
    return idx


def parse(progs, content, id, name, log_not_match=True):
    for idx, p in enumerate(progs):
        m = p.findall(content)
        if m:
            if len(m) > 1:
                log.error('multi-match {} {} ptn-idx={}'.format(id, name, idx))
            if isinstance(m[0], str):
                return m[0].decode('utf8')
            else:
                return m[0]

    if log_not_match:
        log.error('failed to match {} {}'.format(id, name))
    return None


def get_files(cache_files):
    for key, fn in cache_files.items():
        with open(fn, 'r') as fr:
            yield (key, ''.join(fr.readlines()))


def detect_keys(cache_files, ptn, output=None, exclude=set()):
    new_keys = set()
    exclude.update(set(cache_files.keys()))

    log.info('detect keys in {} files'.format(len(cache_files)))

    for key, content in get_files(cache_files):
        new_keys.update(set(ptn.findall(content))-exclude)

    log.info('{} new keys found'.format(len(new_keys)))

    if output:
        with open(output, 'w') as fw:
            fw.write('\n'.join(new_keys))
        log.info('new keys saved in {}'.format(output))
    return new_keys
