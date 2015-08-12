# -*- Encoding: utf-8 -*-
from sqlalchemy import Column, Integer, String

import os
import sys
parent = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent)

from crawler.model import install, BaseModel


class ShopBasic(BaseModel):
    __tablename__ = 'shop_basic'

    sid = Column(String(20), primary_key=True)
    name = Column(String(100))
    star = Column(Integer)
    addr = Column(Integer)

    def __init__(self, sid, name, star, addr):
        self.sid = sid
        self.name = name
        self.star = star
        self.addr = addr


if __name__ == '__main__':
    Session = install('sqlite:///cache/test.sqlite3')
    session = Session()
    session.close()
