# -*- Encoding: utf-8 -*-
import re
import os

from download import RecursiveJob, builk_single

from model import install
from model import Peer


# config
BASE_DIR = os.path.dirname(__file__)
shop_prof_dir = os.path.join(BASE_DIR, 'cache/shop_prof')

for path in [shop_prof_dir]:
    if not os.path.exists(path):
        os.makedirs(path)


class ShopProfPeer(Peer):
    __tablename__ = 'ShopProfPeer'


def grab_shop_prof(session):
    page_name = 'DianPing Shop Profile'
    url = 'http://www.dianping.com/shop/{}'
    sid_ptn = re.compile(r'href="/shop/(\d+)(?:\?[^"]+)?"')
    jobs = RecursiveJob(sid_ptn, ShopProfPeer, session)

    todo = jobs.get_todo()
    while todo:
        print 'grabbing shop prof'
        builk_single(todo, url, shop_prof_dir, jobs.feed, page_name)
        todo = jobs.get_todo()
    else:
        print 'no shop id found'


if __name__ == '__main__':
    Session = install('sqlite:///db_dianping.sqlite3')
    session = Session()

    grab_shop_prof(session)

    session.close()
