# -*- Encoding: utf-8 -*-
import re
import os
import argparse

from download import dl_profile
from parser import parse, get_files, cache_idx, detect_keys

from db import install, shop_profile, shop_cate, shop_reviews

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

_cate_progs = [
    re.compile(r'<div class="breadcrumb">(.*?)</div>', re.DOTALL),
    ]
_cate_field_progs = re.compile(r'>\s*([^<>]+?)\s*(?:</a>|</span>)', re.DOTALL)

_shop_id_ptn = re.compile(r'href="/shop/(\d+)(?:\?[^"]+)?"')
user_id_ptn = re.compile(r'href="/member/(\d+)"')


_review_ptn = re.compile(r'<li[^>]+id="rev_(\d+)"(.+?)<span class="time">(.*?)</span>.*?</li>', re.DOTALL)

_comment_entry_ptns = [
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

_comment_rec_ptns = [
    re.compile(r'<dl class="recommend-info clearfix">(.*?)</dl>', re.DOTALL),  # class="content"
    re.compile(r'<div class="comment-recommend">(.*?)</div>', re.DOTALL),  # class="comment-text"
    re.compile(r'<div class="comment-unit">\s*<ul>\s*(.*\S)\s*</ul>\s*</div>', re.DOTALL),  # class="comment-entry"
    ]

_comment_user_ptns = [
    re.compile(r'class="user-info">\s*<a.*?href="/member/(\d+)".*?>(.*?)</a>', re.DOTALL),
    re.compile(r'<p class="name">\s*<a.*?href="/member/(\d+)".*?>(.*?)</a>', re.DOTALL),
    ]

_comment_star_ptns = [
    re.compile(r'-str(\d+)'),
    re.compile(r'-star(\d+)'),
    ]


shop_star = lambda c, sid: int(parse(_star_ptns, c, sid, 'shop star') or 0)
shop_name = lambda c, sid: parse(_name_ptns, c, sid, 'shop name') or ''
shop_addr = lambda c, sid: parse(_addr_ptns, c, sid, 'shop addr') or ''

comment_entry = lambda c, id: parse(_comment_entry_ptns, c, id, 'comment entry') or ''
comment_rec = lambda c, id: parse(_comment_rec_ptns, c, id, 'comment recommend', log_not_match=False) or ''
comment_user = lambda c, id: parse(_comment_user_ptns, c, id, 'comment user')
comment_star = lambda c, id: int(parse(_comment_star_ptns, c, id, 'comment star') or 0)


def save_shop_basic(cache_files, session):
    exclude = [item.sid for item in session.query(shop_profile).all()]
    data = [shop_profile(sid, shop_name(c, sid), shop_star(c, sid), shop_addr(c, sid)) for sid, c in get_files(cache_files)]
    session.add_all(data)


def save_shop_cate(cache_files, session):
    for sid, c in get_files(cache_files):
        text = parse(_cate_progs, c, id, 'shop cate') or ''
        tags = set(_cate_field_progs.findall(text)) - {'&raquo;'}
        data = [shop_cate(sid, tag) for tag in tags]
        session.add_all(data)


def save_shop_comment(cache_files, session):
    for sid, c in get_files(cache_files):
        reviews = _review_ptn.findall(c)
        for rev_id, text, rev_time in reviews:
            id = '{}-{}'.format(sid, rev_id)
            uid, username = comment_user(text, id)

            session.add(shop_reviews(
                rev_id=rev_id, sid=sid, uid=uid,
                star=comment_star(text, id),
                entry=comment_entry(text, id),
                recommend=comment_rec(text, id),
                rev_time=rev_time.decode('utf8')
                ))


def build_profile_idx(cache_dir):
    cache_files = cache_idx(dir_shop_profile)




def find_new_shops(cache_files):
    new_keys = detect_keys(cache_files, _shop_id_ptn, file_new_shops)
    print '{} new keys'.format(len(new_keys))


if __name__ == '__main__':
    dir_shop_profile = 'cache/profile'
    fn_shop_profile = os.path.join(dir_shop_profile, '{}.html')
    url_shop_profile = 'http://www.dianping.com/shop/{}'

    file_new_shops = 'data/new-shops.txt'

    args_parser = argparse.ArgumentParser()
    args_parser.add_argument('command', type=str,
            choices={'new_shops', 'dl_shop_profile'})
    args = args_parser.parse_args()

    cmd = args.command

    # cache idx
    cache_files = cache_idx(dir_shop_profile)
    print '{} files exists'.format(len(cache_files))

    if cmd == 'new_shops':
        detect_keys(cache_files, _shop_id_ptn, output=file_new_shops)
    elif cmd == 'dl_shop_profile':
        # get shop id set
        sids = set()
        with open(file_new_shops, 'r') as fp:
            sids = {sid.strip() for sid in fp.readlines()}
        # download profile
        dl_profile(sids, url_shop_profile, fn_shop_profile,
                   validate=shop_name, website='dianping')
    else:
        # find new shops

        Session = install('sqlite:///test.sqlite3')
        session = Session()

        save_shop_basic(cache_files, session)
        save_shop_cate(cache_files, session)
        save_shop_comment(cache_files, session)

        session.commit()
