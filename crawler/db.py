# -*- Encoding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy import text
from sqlalchemy import Sequence
from sqlalchemy.orm import sessionmaker


Base = declarative_base()


class download_job(Base):
    __tablename__ = 'download_job'

    id = Column(Integer, Sequence('job_id_seq'), primary_key=True)
    url = Column(String(500))
    filename = Column(String(100))
    status = Column(String(10))

    def __repr__(self):
        return self.url


class his_shop_review(Base):
    __tablename__ = 'his_shop_review'

    shop_id = Column(Integer, primary_key=True)
    num = Column(Integer)
    run_info = Column(String(10))
    notes = Column(String(500))
    timestamp = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    def __repr__(self):
        return 'shop={}, num={}'.format(self.shop_id, self.num)


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


def shop_review_exists(sid):
    Session = sessionmaker(bind=engine)
    session = Session()
    return session.query(his_shop_review).filter_by(shop_id=sid).count() > 0



engine = create_engine('sqlite:///database.sqlite3')
Base.metadata.create_all(engine)


if __name__ == '__main__':
    # add_one(his_shop_review, shop_id='1111', num=300, run_info='success')

    dataset = [
        his_shop_review(shop_id='222', num=203, run_info='success'),
        his_shop_review(shop_id='333', num=349, run_info='success'),
        his_shop_review(shop_id='444', num=3, run_info='success'),
        ]

    # add_many(dataset)

    print shop_review_exists('222')
    print shop_review_exists('224')
