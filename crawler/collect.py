# -*- Encoding: utf-8 -*-
import os


def build_idx(dir, idx_file, prefix='', subfix='.html'):
    """build idx of files in dir

    """
    validate = lambda fn: fn.startswith(prefix) and fn.endswith(subfix)

    idx_data = [fn[len(prefix): -len(subfix)]  # retrieve id
                for fn in os.listdir(dir) if validate(fn)]
    with open(idx_file, 'w') as fp:
        fp.write('\n'.join(idx_data))


if __name__ == '__main__':
    dir_shop_profile = 'cache/profile'
    idx_shop_profile = 'data/idx-shop-profile.txt'

    build_idx(dir_shop_profile, idx_shop_profile)
