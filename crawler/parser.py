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


star_progs = [
    re.compile(r'<span title="[^">]+?" class="mid-rank-stars mid-str(\d+)"></span>', re.DOTALL),
    re.compile(r'<p class="info shop-star">\s*<span class="mid-rank-stars mid-str(\d+)"></span>', re.DOTALL),
    re.compile(r'<div class="comment-rst">\s*<span title="[^">]+?" class="item-rank-rst [mi]rr-star(\d+)"', re.DOTALL),
    re.compile(r'<div class="brief-info">\s*<span title="[^">]+" class="mid-rank-stars mid-str(\d+)">', re.DOTALL),
    re.compile(r'class="mid-rank-stars mid-str(\d+) item">', re.DOTALL),
    ]

comment_star_progs = [
    re.compile(r'-str(\d+)'),
    re.compile(r'-star(\d+)'),
    ]

name_progs = [
    re.compile(r'<h1 class="shop-name">\s*(.*?)\s*<.*?/h1>', re.DOTALL),
    re.compile(r'<h1 class="shop-title" itemprop="name itemreviewed">(.*?)</h1>', re.DOTALL),
    re.compile(r'<h2 class="market-name">(.*?)</h2>', re.DOTALL),
    re.compile(r'<h1>(.*?)</h1>', re.DOTALL),
    ]


addr_progs = [
    re.compile(r'<span [^>]*?itemprop="street-address"[^>]*?>\s*(.*?)\s*</span>', re.DOTALL),
    re.compile(r'<p class="shop-address">\s*(.*?)\s*<span>.*?</span></p>', re.DOTALL),
    re.compile(r'<div class="shop-addr">.*?</a>(.*?)</span>', re.DOTALL),
    re.compile(r'</a>(.*?)<a class="market-map-btn"', re.DOTALL),
    re.compile(r'<div class="add-all">\s*<span class="info-name">(.*?)</span>', re.DOTALL),
    ]

cate_progs = [
    re.compile(r'<div class="breadcrumb">(.*?)</div>', re.DOTALL),
    ]

comment_time_progs = [
    re.compile(r'<span class="time">(.*?)</span>'),
    ]

comment_entry_progs = [
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

comment_rec_progs = [
    re.compile(r'<dl class="recommend-info clearfix">(.*?)</dl>', re.DOTALL),  # class="content"
    re.compile(r'<div class="comment-recommend">(.*?)</div>', re.DOTALL),  # class="comment-text"
    re.compile(r'<div class="comment-unit">\s*<ul>\s*(.*\S)\s*</ul>\s*</div>', re.DOTALL),  # class="comment-entry"
    ]

user_id_progs = [
    re.compile(r'class="user-info">\s*<a.*?href="/member/(\d+)".*?>(.*?)</a>', re.DOTALL),
    re.compile(r'<p class="name">\s*<a.*?href="/member/(\d+)".*?>(.*?)</a>', re.DOTALL),
    ]


def get_files(files_dir, files_prefix=''):
    for filename in os.listdir(files_dir):
        if filename[:-5] not in ignore and filename.endswith('.html') and filename.startswith(files_prefix):
            with open(os.path.join(files_dir, filename)) as f:
                yield (filename[:-5], ''.join(f.readlines()))


def parse(progs, content, id, name, log_not_match=True):
    for idx, p in enumerate(progs):
        m = p.findall(content)
        if m:
            if len(m) > 1:
                log.error('multi-match {} {}. prog-idx={}'.format(id, name, idx))
            return m[0]

    if log_not_match:
        log.error('failed to match {} {}'.format(id, name))
    return None


def parse_shop_star(content, sid):
    return int(parse(star_progs, content, sid, 'star') or 0)


def parse_shop_name(content, sid):
    return parse(name_progs, content, sid, 'shop name') or ''


def parse_shop_addr(content, sid):
    return parse(addr_progs, content, sid, 'shop addr') or ''


def parse_shop_cate(content, sid):
    ptn = re.compile(r'>\s*([^<>]+?)\s*(?:</a>|</span>)', re.DOTALL)
    cate_str = parse(cate_progs, content, sid, 'shop cate')
    if cate_str:
        return set(ptn.findall(cate_str)) - {'&gt;'}
    else:
        log.error('failed to match {} cate in step2'.format(sid))
    return set()




score0_prog = re.compile(r'<i class="icon star-from item J-star-from"></i>')


def has_score0_notes(content):
    return len(score0_prog.findall(content)) > 0


def has_rev(content):
    return len(re.compile(r'comment-list').findall(content)) > 0


rev_prog = re.compile(r'<li[^>]+id="rev_(\d+)"(.+?)<span class="time">(.*?)</span>.*?</li>', re.DOTALL)


def parse_shop_comment(content, sid):
    ret = rev_prog.findall(content)

    # if has_rev(content) and len(ret) == 0:
    #     print sid  # check if correct comment num parsed
    for rev_id, text, timestamp in ret:
        star = parse(comment_star_progs, text, '{}-{}'.format(sid, rev_id), 'comment star')
        entry = parse(comment_entry_progs, text, '{}-{}'.format(sid, rev_id), 'comment entry')
        recommend = parse(comment_rec_progs, text, '{}-{}'.format(sid, rev_id), 'comment recommend', log_not_match=False)
        uid = parse(user_id_progs, text, '{}-{}'.format(sid, rev_id), 'comment user')

    return ret


if __name__ == '__main__':
    dir_shop_profile = 'cache/profile'

    for sid, content in get_files(dir_shop_profile):
        name = parse_shop_name(content, sid)
        star = parse_shop_star(content, sid)
        addr = parse_shop_addr(content, sid)
        tags = parse_shop_cate(content, sid)  # set of tags
        parse_shop_comment(content, sid)
