# -*- Encoding: utf-8 -*-
import re
import os


def parse_shop(content):
    shop_prog = re.compile(r'href="/shop/(\d+)(?:\?[^"]+)?"', re.DOTALL)
    return set(shop_prog.findall(content))


def get_files(files_dir, files_prefix):
    return [os.path.join(files_dir, f) for f in os.listdir(files_dir) if f.startswith(files_prefix)]


if __name__ == '__main__':

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
    with open('data/shops.txt', 'w') as f:
        f.write('\n'.join(data_shops))
