# -*- Encoding: utf-8 -*-
import re
import os

from download import dl_profile, job_list
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


def dl_shop_prof(pf_cache, use_job_file=False, job_file='.job/dianping-shop-profile-todo.txt'):
    url = 'http://www.dianping.com/shop/{}'
    page_name = 'dianping shop profile'

    sids = set()
    if use_job_file:
        with open(job_file, 'r') as fp:
            sids = {line.strip() for line in fp.readlines()}
        print 'user job file. {} sids loaded'.format(len(sids))
    else:
        sids = detect_keys(cache_idx(pf_cache), _shop_id_ptn)
        print '{} new sids found'.format(len(sids))
        with open(job_file, 'w') as fw:
            fw.write('\n'.join(sids))

    dl_profile(sids, url, pf_cache, validate=shop_name, page_name=page_name)


if __name__ == '__main__':
    test_dir_pf = 'test_data/dl_pf'

    if not os.path.exists(test_dir_pf):
        from download import test_prof
        test_prof(test_dir_pf)

    dl_shop_prof(test_dir_pf, use_job_file=True)

    """
        Session = install('sqlite:///test.sqlite3')
        session = Session()

        save_shop_basic(cache_files, session)
        save_shop_cate(cache_files, session)
        save_shop_comment(cache_files, session)

        session.commit()
    """
