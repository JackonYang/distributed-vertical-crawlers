# -*- Encoding: utf-8 -*-
import re

category_prog = re.compile(r'<a .*?href="(http://www.dianping.com/search/category/[\w/]+)".*?>(.*?)</a>', re.DOTALL)

if __name__ == '__main__':
    pass
