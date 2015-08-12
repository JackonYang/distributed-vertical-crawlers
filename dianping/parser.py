# -*- Encoding: utf-8 -*-
import re
import os

import sys
parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent)

from crawler.model import install
from model import ShopBasic, ShopReview
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

_review_ptn = re.compile(r'<li[^>]+id="rev_(\d+)"(.+?)<span class="time">(.*?)</span>.*?</li>', re.DOTALL)

_rev_entry_ptns = [
    # class="content"
    re.compile(r'<p class="desc J-desc">(.+?)</p>', re.DOTALL),  # 长点评
    re.compile(r'<p class="desc">(.+?)</p>', re.DOTALL),  # 短点评
    # class="comment-entry"
    re.compile(r'<div class="J_extra-cont Hide">(.+?)</div>', re.DOTALL),  # 长点评
    re.compile(r'<div id="review_\d+_summary">(.+?)</div>', re.DOTALL),  # 短点评
    # class="comment-text"
    re.compile(r'<div class="desc J_brief-cont-long Hide">\s*(.+?)\s*</div>', re.DOTALL),  # 长点评
    re.compile(r'<div class="(?:desc )?J_brief-cont">\s*(.+?)\s*</div>', re.DOTALL),  # 长点评
    ]

_rev_recommend_ptns = [
    re.compile(r'<dl class="recommend-info clearfix">(.*?)</dl>', re.DOTALL),  # class="content"
    re.compile(r'<div class="comment-recommend">(.*?)</div>', re.DOTALL),  # class="comment-text"
    re.compile(r'<div class="comment-unit">\s*<ul>\s*(.*\S)\s*</ul>\s*</div>', re.DOTALL),  # class="comment-entry"
    ]

_rev_user_ptns = [
    re.compile(r'class="user-info">\s*<a.*?href="/member/(\d+)".*?>(.*?)</a>', re.DOTALL),
    re.compile(r'<p class="name">\s*<a.*?href="/member/(\d+)".*?>(.*?)</a>', re.DOTALL),
    ]

_rev_star_ptns = [
    re.compile(r'-str(\d+)'),
    re.compile(r'-star(\d+)'),
    ]


rev_entry = lambda c, id: parse(_rev_entry_ptns, c, id, 'review entry') or ''
rev_rec = lambda c, id: parse(_rev_recommend_ptns, c, id, 'review recommend', log_not_match=False) or ''
rev_user = lambda c, id: parse(_rev_user_ptns, c, id, 'review user')
rev_star = lambda c, id: int(parse(_rev_star_ptns, c, id, 'review star') or 0)


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


def save_shop_review(session, shop_prof_dir):
    parsed = {i.sid for i in session.query(ShopReview).distinct().all()}
    print '{} shop reviews parsed'.format(len(parsed))

    data = []

    for sid, c in read_file(shop_prof_dir, parsed, lambda fn: fn[:-5]):
        reviews = _review_ptn.findall(c)
        for rev_id, text, rev_time in reviews:
            id = '{}-{}'.format(sid, rev_id)
            uid, username = rev_user(text, id)

            data.append(ShopReview(
                rev_id=rev_id, sid=sid, uid=uid,
                star=rev_star(text, id), entry=rev_entry(text, id),
                recommend=rev_rec(text, id), rev_time=rev_time))

    session.add_all(data)
    session.commit()


if __name__ == '__main__':
    BASE_DIR = os.path.dirname(__file__)
    shop_prof_dir = os.path.join(BASE_DIR, 'cache/shop_prof')

    Session = install('sqlite:///cache/dianping.sqlite3')
    session = Session()

    save_shop_basic(session, shop_prof_dir)
    save_shop_review(session, shop_prof_dir)

    session.close()
