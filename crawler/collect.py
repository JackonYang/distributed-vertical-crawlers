# -*- Encoding: utf-8 -*-
import os
import re

from log4f import debug_logger

log = debug_logger('log/collect', 'collect')


def build_idx(dir, idx_file, prefix='', subfix='.html'):
    """build idx of files in dir

    """
    validate = lambda fn: fn.startswith(prefix) and fn.endswith(subfix)

    idx_data = {fn[len(prefix): -len(subfix)]: os.path.join(dir, fn)
                for fn in os.listdir(dir) if validate(fn)}
    with open(idx_file, 'w') as fp:
        fp.write('\n'.join(idx_data.keys()))
    return idx_data


def detect(files, ptn, olds, obj_name='', idx_file='data/idx-shop-todo.txt'):

    total = set()
    for fn in files:
        with open(fn, 'r') as fp:
            content = ''.join(fp.readlines())
            total.update(set(ptn.findall(content)))

    news = set(total) - set(olds)
    with open(idx_file, 'w') as fp:
        fp.write('\n'.join(news))
    log_str = '{}/{}(new/total), new {} ID saved in {}'
    log.info(log_str.format(len(news), len(total), obj_name, idx_file))
    return news


if __name__ == '__main__':
    dir_shop_profile = 'cache/profile'
    idx_shop_profile = 'data/idx-shop-profile.txt'

    # step 1, build idx
    shops = build_idx(dir_shop_profile, idx_shop_profile)

    shop_id_ptn = re.compile(r'href="/shop/(\d+)(?:\?[^"]+)?"')
    new_shops = detect(shops.values(), shop_id_ptn, shops.keys(), obj_name='shop')
