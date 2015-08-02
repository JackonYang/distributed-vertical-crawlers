# -*- Encoding: utf-8 -*-
import matplotlib.pyplot as plt

from sqlalchemy.orm import sessionmaker
from db import shop_profile, engine

def shop_star():
    Session = sessionmaker(bind=engine)
    session = Session()
    return [s.star for s in session.query(shop_profile).all()]


def lvl_count(data):
    count = dict()
    for i in data:
        if i in count:
            count[i] += 1
        else:
            count[i] = 1
    return sorted(count.items(), key=lambda d: d[0])


def plot_star_stat(stat, total):
    k = [d[0]/10.0 for d in stat]
    v = [d[1] for d in stat]

    plt.plot(k, v, '-*')
    plt.title(u'score distribution of {} shops'.format(total))
    plt.xlabel(u'score')
    plt.ylabel(u'number')
    plt.show()


if __name__ == '__main__':
    stars = shop_star()
    stat = lvl_count(stars)
    plot_star_stat(stat, len(stars))

