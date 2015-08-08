# -*- Encoding: utf-8 -*-
import re
import os

from parser import parse, detect

from db import install, shop_profile, shop_tags, shop_reviews

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

cate_progs = [
    re.compile(r'<div class="breadcrumb">(.*?)</div>', re.DOTALL),
    ]
cate_field_progs = re.compile(r'>\s*([^<>]+?)\s*(?:</a>|</span>)', re.DOTALL)

shop_id_ptn = re.compile(r'href="/shop/(\d+)(?:\?[^"]+)?"')
user_id_ptn = re.compile(r'href="/member/(\d+)"')


review_ptn = re.compile(r'<li[^>]+id="rev_(\d+)"(.+?)<span class="time">(.*?)</span>.*?</li>', re.DOTALL)

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


def parse_shop_cate(content, sid):
    cate_str = parse(cate_progs, content, sid, 'shop cate') or ''
    return set(cate_field_progs.findall(cate_str)) - {'&gt;'}


def parse_shop_comment(content, sid):
    reviews = review_ptn.findall(content)

    ret = []
    for rev_id, text, rev_time in reviews:
        id = '{}-{}'.format(sid, rev_id)
        uid, username = comment_user(text, id)

        ret.append(shop_reviews(
            rev_id=rev_id,
            sid=sid,
            uid=uid,
            star=comment_star(text, id),
            entry=comment_entry(text, id),
            recommend=comment_rec(text, id),
            rev_time=rev_time.decode('utf8')
            ))
    return ret


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

    basic_info = []
    tags = []
    revs = []
    sids = set()

    c = None
    for sid, fn in files.items():
        # read
        with open(fn, 'r') as fr:
            c = ''.join(fr.readlines())
        # write
        sids.update(set(detect(c, shop_id_ptn)))
        basic_info.append(shop_profile(sid=sid, name=shop_name(c, sid), star=shop_star(c, sid), addr=shop_addr(c, sid)))
        tags.extend([shop_tags(sid=sid, tag=t) for t in parse_shop_cate(c, sid)])
        revs.extend(parse_shop_comment(c, sid))
        if len(basic_info) % 1000 == 0:
            print len(basic_info)

    news = sids - set(files.keys())
    with open('new-shop-id.txt', 'w') as fp:
        fp.write('\n'.join(news))
    print '{}/{}(new/total) shops found'.format(len(news), len(sids))

    Session = install()
    session = Session()
    session.add_all(basic_info)
    session.add_all(tags)
    session.add_all(revs)
    session.commit()
    print 'saved. {} shop basic info. {} shop tags. {} reviews'.format(len(basic_info), len(tags), len(revs))


if __name__ == '__main__':
    dir_shop_profile = 'cache/profile'
    parse_shop_profile(dir_shop_profile)
