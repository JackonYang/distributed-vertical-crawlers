# -*- Encoding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy import text
from sqlalchemy import Sequence
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class job_shop_review(Base):
    __tablename__ = 'job_shop_review'

    id = Column(Integer, Sequence('job_shop_review_seq'), primary_key=True)
    sid = Column(Integer)
    num = Column(Integer)
    timestamp = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    notes = Column(String(500), default='')

    def __repr__(self):
        return '<job_shop_review(shop={}, num={})>'.format(self.sid, self.num)


class shop_profile(Base):
    __tablename__ = 'shop_profile'

    sid = Column(Integer, primary_key=True)
    shop_name = Column(String(100))
    star = Column(Integer)
    timestamp = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))


    def __repr__(self):
        return '<shop_profile({}-{})>'.format(self.sid, self.shop_name)


engine = create_engine('sqlite:///database.sqlite3')
Base.metadata.create_all(engine)


def add_one(table, *args, **kwargs):
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add(table(*args, **kwargs))
    session.commit()


def add_many(obj_list):
    Session = sessionmaker(bind=engine)
    session = Session()
    session.add_all(obj_list)
    session.commit()


def exists(table, *args, **kwargs):
    Session = sessionmaker(bind=engine)
    session = Session()
    return session.query(table).filter_by(*args, **kwargs).count() > 0


if __name__ == '__main__':
    add_one(job_shop_review, sid='1111', num=300)
    add_one(job_shop_review, sid='222', num=509)

    print exists(job_shop_review, sid='222')
    print exists(job_shop_review, sid='224')
