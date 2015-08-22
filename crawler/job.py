# -*- Encoding: utf-8 -*-
import re
import os
import time 
import json

from os.path import join




class JobPool:
    def __init__(self, db, cache_root, job_name, pagination=True, subfix='.html', timeout=10):
        self.cache_dir = join(cache_root, job_name)
        self.job_file = join(cache_root, 'job_{}.json'.format(job_name))

        self.subfix = subfix
        self.timeout = timeout
        self.key = lambda fn: fn[:fn.find('_')] if pagination \
            else lambda fn: fn[:-5]

        self.data = self._load()

        self.db = db
        self.total_tbl = '{}:total'.format(job_name)
        self.todo_tbl = '{}:todo'.format(job_name)

    def scan(self, path, ptn, save_period=2000):
        total = set(os.listdir(path))
        todo = total - set(self.data.keys())
        print '{}/{} to parse.'.format(len(todo), len(total))

        for i, filename in enumerate(todo):
            with open(join(path, filename)) as f:
                c = ''.join(f.readlines())
            self.data[filename] = ptn.findall(c)

            if i % save_period == 0:
                print 'saving. {} done.'.format(i+1)
                self._save()

        self._save()

    def init_db(self, total):
        # todo: clear table
        self.db.sadd(self.total_tbl, *total)
        todo = set(total) - self._done()
        self.db.rpush(self.todo_tbl, *todo)

    def next(self):
        key = self.db.blpop(self.todo_tbl, self.timeout)
        return key and key[1]

    def add(self, *keys):
        count = 0
        for key in keys:
            if self.db.sadd(self.total_tbl, key):
                self.db.rpush(self.todo_tbl, key)
                count += 1
        return count

    def add_force(self, *keys):
        self.db.rpush(self.todo_tbl, *key)
        return self.db.sadd(self.total_tbl, *key)

    def _load(self):
        data = dict()
        if os.path.exists(self.job_file):
            with open(self.job_file, 'r') as fr:
                data = json.load(fr)
        return data

    def _save(self):
        with open(self.job_file, 'wb') as fw:
            json.dump(self.data, fw, indent=4)

    def _done(self):
        return {self.key(fn)
                for fn in os.listdir(self.cache_dir) if fn.endswith(self.subfix)}


if __name__ == '__main__':

    import redis
    r = redis.StrictRedis()
    cache_root = '../dianping/cache'
    job_name = 'shop_review'
    repo = JobPool(r, cache_root, job_name, pagination=True)

    shop_prof_dir = '../dianping/cache/shop_prof'
    ptn = re.compile(r'<li[^>]+id="rev_(\d+)"')
    repo.scan(shop_prof_dir, ptn)

    total = {key[:-5] for key, vs in repo.data.items() if len(vs) > 9}
    repo.init_db(total)

    key = repo.next()
    i = 0
    while key:
        i += 1
        print key
        key = repo.next()
    print i
