# -*- Encoding: utf-8 -*-
import re
import os
import shutil

from download import RecursiveJob, builk_single

from model import install
from model import Peer


class ProfilePeer(Peer):
    """ model for test_builk_single

    """
    __tablename__ = 'ProfilePeer'


def init_test_path():
    path = 'test_data'
    if os.path.exists(path):
        shutil.rmtree(path)
    os.makedirs(path)
    return path


def test_builk_single():

    init_test_path()
    path = 'test_data/single'
    os.makedirs(path)
    db = 'sqlite:///test_data/single.sqlite3'

    keys = ['22949597', '24768319', '22124523']
    url_ptn = 'http://www.dianping.com/shop/{}'
    page_name = 'dianping shop profile'
    item_ptn = re.compile(r'href="/shop/(\d+)(?:\?[^"]+)?"')

    Session = install(db)
    session = Session()

    jobs = RecursiveJob(item_ptn, ProfilePeer, session)
    builk_single(keys, url_ptn, path, page_name=page_name)
    jobs.build_idx(path, lambda fn: fn.endswith('.html') and fn[:-5])
    builk_single(keys, url_ptn, path, jobs.feed, page_name=page_name)
    builk_single(jobs.get_todo(), url_ptn, path, jobs.feed, page_name)

    session.close()


if __name__ == '__main__':
    test_builk_single()
