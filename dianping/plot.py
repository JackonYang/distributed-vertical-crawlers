# -*- Encoding: utf-8 -*-
import matplotlib.pyplot as plt

from grab import ShopReviewCnt
from crawler.model import install


def aggressive(data):
    lvl_data = dict()
    for i in data:
        if i in lvl_data:
            lvl_data[i] += 1
        else:
            lvl_data[i] = 1
    return sorted(lvl_data.items(), key=lambda d: d[0])


def plot_stat(stat, total, name):
    k = [d[0] for d in stat]
    v = [d[1] for d in stat]

    plt.plot(k, v, '-*')
    plt.title('{} distribution of {} shops'.format(name, total))
    plt.xlabel(name)
    plt.ylabel('number')
    plt.show()


def shop_rev(session):
    rev_cnt = [item.count for item in session.query(ShopReviewCnt).all()]
    plot_stat(aggressive(rev_cnt), len(rev_cnt),
              'shop reviews count')


if __name__ == '__main__':
    db_pf = 'sqlite:///cache/db_profile.sqlite3'
    Session = install(db_pf)
    session = Session()

    shop_rev(session)

    session.close()
