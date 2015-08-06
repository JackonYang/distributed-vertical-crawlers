# -*- Encoding: utf-8 -*-
import re
import os

from log4f import debug_logger

log = debug_logger('log/parser', 'parser')

ignore = {
    '15923760': u'商户不存在',
    '21411682': u'没有评分数据',
    }


star_progs = [
    re.compile(r'<span title="[^">]+?" class="mid-rank-stars mid-str(\d+)"></span>', re.DOTALL),
    re.compile(r'<p class="info shop-star">\s*<span class="mid-rank-stars mid-str(\d+)"></span>', re.DOTALL),
    re.compile(r'<div class="comment-rst">\s*<span title="[^">]+?" class="item-rank-rst [mi]rr-star(\d+)"', re.DOTALL),
    re.compile(r'<div class="brief-info">\s*<span title="[^">]+" class="mid-rank-stars mid-str(\d+)">', re.DOTALL),
    re.compile(r'class="mid-rank-stars mid-str(\d+) item">', re.DOTALL),
    ]

name_progs = [
    re.compile(r'<h1 class="shop-name">\s*(.*?)\s*<.*?/h1>', re.DOTALL),
    re.compile(r'<h1 class="shop-title" itemprop="name itemreviewed">(.*?)</h1>', re.DOTALL),
    re.compile(r'<h2 class="market-name">(.*?)</h2>', re.DOTALL),
    re.compile(r'<h1>(.*?)</h1>', re.DOTALL),
    ]


def get_files(files_dir, files_prefix=''):
    for filename in os.listdir(files_dir):
        if filename[:-5] not in ignore and filename.endswith('.html') and filename.startswith(files_prefix):
            with open(os.path.join(files_dir, filename)) as f:
                yield (filename[:-5], ''.join(f.readlines()))


def parse(progs, content, id, name):
    for idx, p in enumerate(progs):
        m = p.findall(content)
        if m:
            if len(m) > 1:
                log.error('multi-match {} {}. prog-idx={}'.format(id, name, idx))
            return m[0]
    log.error('failed to match {} {}'.format(id, name))
    return None


def parse_shop_star(content, sid):
    return int(parse(star_progs, content, sid, 'star') or 0)


def parse_shop_name(content, sid):
    return parse(name_progs, content, sid, 'shop name') or ''



if __name__ == '__main__':
    dir_shop_profile = 'cache/profile'

    for sid, content in get_files(dir_shop_profile):
        name = parse_shop_name(content, sid)
        star = parse_shop_star(content, sid)
