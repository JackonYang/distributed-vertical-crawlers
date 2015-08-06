# -*- Encoding: utf-8 -*-
import re
import os

from db import shop_profile, add_many, get_sids_db


def find_shop_ids(content):
    shop_prog = re.compile(r'href="/shop/(\d+)(?:\?[^"]+)?"', re.DOTALL)
    return set(shop_prog.findall(content))


def get_files(files_dir, files_prefix=''):
    for filename in os.listdir(files_dir):
        if filename.endswith('.html') and filename.startswith(files_prefix):
            with open(os.path.join(files_dir, filename)) as f:
                yield (filename[:-5], ''.join(f.readlines()))


def parse_shop_star(content):
    progs = [
        r'class="mid-rank-stars mid-str(\d+)"',
        r'item-rank-rst irr-star(\d+)',
        r'item-rank-rst mrr-star(\d+)',  # 21733328
        r'mid-rank-stars mid-str(\d+)', # 2406454
        ]
    for p in progs:
        m = re.compile(p, re.DOTALL).findall(content)
        if m:
            return int(m[0])
    return 0


def parse_shop_name(content):
    progs = [
        r'<h1 class="shop-name">\s*(.*?)\s*<.*?/h1>',
        r'<h1 class="shop-title" itemprop="name itemreviewed">(.*?)</h1>',  # sid 17936881
        r'<h2 class="market-name">(.*?)</h2>',  # sid 1804816
        r'<h1>(.*?)</h1>',  # sid 19662907
        ]
    for p in progs:
        m = re.compile(p, re.DOTALL).findall(content)
        if m:
            return m[0].decode('utf8')
    return 'null'


if __name__ == '__main__':
    dir_shop_profile = 'cache/shops'

    data_shop_profile = []

    searched = get_sids_db()

    for sid, content in get_files(dir_shop_profile):
        # shop profile
        if sid not in searched:
            name = parse_shop_name(content)
            star = parse_shop_star(content)
            data_shop_profile.append(shop_profile(sid=sid, shop_name=name, star=star))

    add_many(data_shop_profile)
    print '{} new shop profile saved'.format(len(data_shop_profile))
