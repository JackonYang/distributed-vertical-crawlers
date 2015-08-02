# -*- Encoding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy import text
from sqlalchemy import Sequence
from sqlalchemy.orm import sessionmaker


Old = declarative_base()

class his_shop_review(Old):
    __tablename__ = 'his_shop_review'

    shop_id = Column(Integer, primary_key=True)
    num = Column(Integer)
    run_info = Column(String(10))
    notes = Column(String(500))
    timestamp = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    def __repr__(self):
        return 'shop={}, num={}'.format(self.shop_id, self.num)


New = declarative_base()

class job_shop_review(New):
    __tablename__ = 'job_shop_review'

    id = Column(Integer, Sequence('job_shop_review_seq'), primary_key=True)
    sid = Column(Integer)
    num = Column(Integer)
    timestamp = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))
    notes = Column(String(500), default='')

    def __repr__(self):
        return '<job_shop_review(shop={}, num={})>'.format(self.sid, self.num)


if __name__ == '__main__':

    # output
    old_engine = create_engine('sqlite:///database.sqlite3')
    Old_Session = sessionmaker(bind=old_engine)
    old = Old_Session()

    # convert
    data = [job_shop_review(sid=obj.shop_id, num=obj.num, timestamp=obj.timestamp) for obj in old.query(his_shop_review).all()]

    # init new table
    new_engine = create_engine('sqlite:///database2.sqlite3')
    New.metadata.create_all(new_engine)

    print len(data)

    # commit data to new table
    New_Session = sessionmaker(bind=new_engine)
    new = New_Session()
    new.add_all(data)
    new.commit()
