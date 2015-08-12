# -*- Encoding: utf-8 -*-
import re
import os

from log4f import debug_logger

log = debug_logger('log/parser', 'parser')


def parse(progs, content, id, name, log_not_match=True, default=''):
    for idx, p in enumerate(progs):
        m = p.findall(content)
        if m:
            if len(m) > 1:
                log.error('multi-match {} {} ptn-idx={}'.format(id, name, idx))
            return m[0]

    if log_not_match:
        log.error('failed to match {} {}'.format(id, name))
    return default


def read_file(path, exclude, key):
    files = {key(fn): fn
             for fn in os.listdir(path) if key(fn) not in exclude}
    for sid, fn in files.items():
        with open(os.path.join(path, fn), 'r') as f:
            yield (sid, ''.join(f.readlines()).decode('utf8'))
