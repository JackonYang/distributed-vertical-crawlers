# -*- Encoding: utf-8 -*-
import re
import os


def parse_shop(content):
    shop_prog = re.compile(r'href="/shop/(\d+)(?:\?[^"]+)?"', re.DOTALL)
    return set(shop_prog.findall(content))


def get_files(files_dir, files_prefix=''):
    return [[f[:-5], os.path.join(files_dir, f)] for f in os.listdir(files_dir) if f.endswith('.html') and f.startswith(files_prefix)]


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
            return m[0]
    return ''


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
            return m[0]
    return ''


if __name__ == '__main__':

    """
    data_shops = set()
    # category parser
    for fname in get_files('cache/category', 'category_'):
        with open(fname, 'r') as f:
            content = ''.join(f.readlines())

            shops = parse_shop(content)
            if shops:
                data_shops = data_shops.union(shops)
            else:
                print '0 shops got in {}'.format(fname)
    print '\n'.join(data_shops)
    """

    for sid, fname in get_files('cache/shops'):
        with open(fname, 'r') as f:
            content = ''.join(f.readlines())

            name = parse_shop_name(content)
            star = parse_shop_star(content)
            print sid, name, star
