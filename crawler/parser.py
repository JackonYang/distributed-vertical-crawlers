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



comment_time_progs = [
    re.compile(r'<span class="time">(.*?)</span>'),
    ]


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


score0_prog = re.compile(r'<i class="icon star-from item J-star-from"></i>')


def has_score0_notes(content):
    return len(score0_prog.findall(content)) > 0


def has_rev(content):
    return len(re.compile(r'comment-list').findall(content)) > 0
