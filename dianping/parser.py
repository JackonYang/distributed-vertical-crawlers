# -*- Encoding: utf-8 -*-
import re
import os

import sys
parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent)

from crawler.model import install
from model import ShopBasic
from crawler.parser import parse, read_file


star_ptns = [
    re.compile(r'<span title="[^">]+?" class="mid-rank-stars mid-str(\d+)"></span>', re.DOTALL),
    re.compile(r'<p class="info shop-star">\s*<span class="mid-rank-stars mid-str(\d+)"></span>', re.DOTALL),
    re.compile(r'<div class="comment-rst">\s*<span title="[^">]+?" class="item-rank-rst [mi]rr-star(\d+)"', re.DOTALL),
    re.compile(r'<div class="brief-info">\s*<span title="[^">]+" class="mid-rank-stars mid-str(\d+)">', re.DOTALL),
    re.compile(r'class="mid-rank-stars mid-str(\d+) item">', re.DOTALL),
    ]

name_ptns = [
    re.compile(r'<h1 class="shop-name">\s*(.*?)\s*<.*?/h1>', re.DOTALL),
    re.compile(r'<h1 class="shop-title" itemprop="name itemreviewed">(.*?)</h1>', re.DOTALL),
    re.compile(r'<h2 class="market-name">(.*?)</h2>', re.DOTALL),
    re.compile(r'<h1>(.*?)</h1>', re.DOTALL),
    ]

addr_ptns = [
    re.compile(r'<span [^>]*?itemprop="street-address"[^>]*?>\s*(.*?)\s*</span>', re.DOTALL),
    re.compile(r'<p class="shop-address">\s*(.*?)\s*<span>.*?</span></p>', re.DOTALL),
    re.compile(r'<div class="shop-addr">.*?</a>(.*?)</span>', re.DOTALL),
    re.compile(r'</a>([<>]+?)<a class="market-map-btn"', re.DOTALL),
    re.compile(r'<div class="add-all">\s*<span class="info-name">(.*?)</span>', re.DOTALL),
    ]


def star(c, sid):
    return int(parse(star_ptns, c, sid, 'shop star', default=0))


def name(c, sid):
    return parse(name_ptns, c, sid, 'shop name')


def addr(c, sid):
    return parse(addr_ptns, c, sid, 'shop addr')


def save_shop_basic(session, shop_prof_dir):

    parsed = {i.sid for i in session.query(ShopBasic).distinct().all()}
    print '{} shop basic parsed'.format(len(parsed))
    data = [ShopBasic(sid, name(c, sid), star(c, sid), addr(c, sid)) 
            for sid, c in read_file(shop_prof_dir, parsed, lambda fn: fn[:-5])]
    print '{} shop basic to saved'.format(len(data))

    session.add_all(data)
    session.commit()


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(__file__)
    shop_prof_dir = os.path.join(BASE_DIR, 'cache/shop_prof')

    Session = install('sqlite:///cache/dianping.sqlite3')
    session = Session()

    save_shop_basic(session, shop_prof_dir)

    session.close()
