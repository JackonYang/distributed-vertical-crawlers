# -*- Encoding: utf-8 -*-
import re
import os
import json

from log4f import debug_logger

log = debug_logger('log/parser', 'crawler.parser')


class Indexing:
    def __init__(self, ptn, filename):
        self.ptn = ptn
        self.filename = filename

        self.data = dict()
        if os.path.exists(filename):
            with open(self.filename, 'r') as fr:
                self.data = json.load(fr)

    def save(self):
        with open(self.filename, 'wb') as fw:
            json.dump(self.data, fw, indent=4)

    def scan(self, path, save_period=2000):
        total = set(os.listdir(path))
        todo = total - set(self.data.keys())
        print '{}/{} to parse.'.format(len(todo), len(total))

        for i, filename in enumerate(todo):
            with open(os.path.join(path, filename)) as f:
                c = ''.join(f.readlines())
            self.data[filename] = self.ptn.findall(c)

            if i % save_period == 0:
                print 'saving. {} done.'.format(i+1)
                self.save()


def parse(progs, content, id, name, log_not_match=True, default=''):
    for idx, p in enumerate(progs):
        m = p.findall(content)
        if m:
            if len(m) > 1:
                log.error('multi-match {} {} ptn-idx={}'.format(id, name, idx))
            return m[0]

    if log_not_match:
        log.error('failed to match {} {}'.format(id, name))
    return default


def read_file(path, exclude, key):
    files = {key(fn): fn
             for fn in os.listdir(path) if key(fn) not in exclude}
    print '{} new files'.format(len(files))
    for sid, fn in files.items():
        with open(os.path.join(path, fn), 'r') as f:
            yield (sid, ''.join(f.readlines()).decode('utf8'))


if __name__ == '__main__':
    uid_ptn = re.compile(r'href="/member/(\d+)(?:\?[^"]+)?"')
    Indexing(uid_ptn, '../dianping/cache/uid.json').scan('../dianping/cache/shop_prof')
