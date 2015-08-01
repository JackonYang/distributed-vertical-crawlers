# -*- Encoding: utf-8 -*-
import re
import socket
from httplib2 import Http


_headers_templates = {
    'Connection': 'keep-alive',
    'User-Agent': ('Mozilla/5.0 (Windows NT 6.1) AppleWebKit/534.24 '
                   '(KHTML, like Gecko) Chrome/11.0.696.65 Safari/534.24'),
    'Content-type': 'application/x-www-form-urlencoded',
    'Accept': '*/*',
    'Accept-Charset': 'UTF-8,*;q=0.5',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
}


def get_header():
    return _headers_templates.copy()


def request(url, timeout=2, method='GET'):
    """return None if timeout"""
    h = Http(timeout=timeout)
    try:
        rsp, content = h.request(url, method, headers=get_header())
    except socket.timeout:
        return None

    if rsp['status'] != '404':  # TODO; status code check
        return content


def request_pages(target, page_range=100, filename=None):
    """request a list of pages

    page_range is a set / list of pages to request.
       if int, [1, page_range] will be generated.
    """
    if isinstance(page_range, int):
        page_range = range(1, page_range+1)

    # request next page until no more items detected
    for page in page_range:
        content = request(target.url(page))
        if not target.parse(content, page):
            break

    resend_pages = target.get_resend()
    if resend_pages:
        request_pages(target, resend_pages)


class Pagination:
    def __init__(self, url_ptn, item_ptn, max_failed=5):
        self.url_ptn = url_ptn
        self.item_ptn = item_ptn
        self.max_failed = max_failed

        self.data = []
        self.failed_seq = set()

    def url(self, page):
        return self.url_ptn.format(page)

    def parse(self, content, page):
        if content is None:  # Error
            self.failed_seq.add(page)
            return self.go_on()

        items = self.item_ptn.findall(content)
        if not items:
            return False

        self.data.extend(items)
        return True

    def go_on(self):
        return len(self.failed_seq) <= self.max_failed

    def get_resend(self):
        if self.failed_seq and self.go_on():
            return self.failed_seq
        return None


if __name__ == '__main__':

    review_item_ptn = re.compile(r'<a target="_blank" title="" href="/member/(\d+)">(.+?)</a>')

    shop_id = '16005090'
    review_url_ptn = ''.join([
        'http://www.dianping.com/shop/',
        shop_id,
        '/review_more?pageno={}',
        ])
    target = Pagination(review_url_ptn, review_item_ptn)

    request_pages(target, 10)

    for pid, name in target.data:
        print pid, name
    print len(target.data)
