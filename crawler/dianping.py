# -*- Encoding: utf-8 -*-
import re
import os

from parser import parse

from db import install, shop_profile

_star_ptns = [
    re.compile(r'<span title="[^">]+?" class="mid-rank-stars mid-str(\d+)"></span>', re.DOTALL),
    re.compile(r'<p class="info shop-star">\s*<span class="mid-rank-stars mid-str(\d+)"></span>', re.DOTALL),
    re.compile(r'<div class="comment-rst">\s*<span title="[^">]+?" class="item-rank-rst [mi]rr-star(\d+)"', re.DOTALL),
    re.compile(r'<div class="brief-info">\s*<span title="[^">]+" class="mid-rank-stars mid-str(\d+)">', re.DOTALL),
    re.compile(r'class="mid-rank-stars mid-str(\d+) item">', re.DOTALL),
    ]

_name_ptns = [
    re.compile(r'<h1 class="shop-name">\s*(.*?)\s*<.*?/h1>', re.DOTALL),
    re.compile(r'<h1 class="shop-title" itemprop="name itemreviewed">(.*?)</h1>', re.DOTALL),
    re.compile(r'<h2 class="market-name">(.*?)</h2>', re.DOTALL),
    re.compile(r'<h1>(.*?)</h1>', re.DOTALL),
    ]

_addr_ptns = [
    re.compile(r'<span [^>]*?itemprop="street-address"[^>]*?>\s*(.*?)\s*</span>', re.DOTALL),
    re.compile(r'<p class="shop-address">\s*(.*?)\s*<span>.*?</span></p>', re.DOTALL),
    re.compile(r'<div class="shop-addr">.*?</a>(.*?)</span>', re.DOTALL),
    re.compile(r'</a>([<>]+?)<a class="market-map-btn"', re.DOTALL),
    re.compile(r'<div class="add-all">\s*<span class="info-name">(.*?)</span>', re.DOTALL),
    ]


def cache_idx(dir, prefix='', subfix='.html'):
    """build idx of cache files in dir.
    
    return {key-id: abs filename}
    """
    validate = lambda fn: fn.startswith(prefix) and fn.endswith(subfix)
    key = lambda fn: fn[len(prefix): -len(subfix)]

    return {key(fn): os.path.join(dir, fn)
            for fn in os.listdir(dir) if validate(fn)}


def parse_shop_profile(dir, token=';'):
    files = cache_idx(dir)
    print '{} files exists'.format(len(files))

    shop_star = lambda c, sid: int(parse(_star_ptns, c, sid, 'shop star') or 0)

    shop_name = lambda c, sid: parse(_name_ptns, c, sid, 'shop name') or ''

    shop_addr = lambda c, sid: parse(_addr_ptns, c, sid, 'shop addr') or ''

    data = []
    c = None
    for sid, fn in files.items():
        # read
        with open(fn, 'r') as fr:
            c = ''.join(fr.readlines())
        data.append(shop_profile(sid=sid, name=shop_name(c, sid), star=shop_star(c, sid), addr=shop_addr(c, sid)))

    Session = install()
    session = Session()
    session.add_all(data)
    session.commit()
    print '{} shop basic info saved'.format(len(data))

if __name__ == '__main__':
    dir_shop_profile = 'cache/profile'
    parse_shop_profile(dir_shop_profile)
