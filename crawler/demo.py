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
    pf_path = 'test_data/dl_pf'
    os.makedirs(pf_path)
    pf_db = 'sqlite:///test_data/test_builk_single.sqlite3'

    keys = ['22949597', '24768319', '22124523']
    url_pf = 'http://www.dianping.com/shop/{}'
    page_name = 'dianping shop profile'
    sid_ptn = re.compile(r'href="/shop/(\d+)(?:\?[^"]+)?"')

    Session = install(pf_db)
    session = Session()

    jobs = RecursiveJob(sid_ptn, ProfilePeer, session)
    # builk_single(keys, url_pf, testdir_pf, page_name=page_name)
    jobs.build_idx(pf_path, lambda fn: fn.endswith('.html') and fn[:-5])

    builk_single(keys, url_pf, pf_path, jobs.feed, page_name=page_name)

    builk_single(jobs.get_todo(), url_pf, pf_path, jobs.feed, page_name)

    session.close()


if __name__ == '__main__':
    test_builk_single()
