# -*- Encoding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy import text, Sequence

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


Base = declarative_base()
engine = None


class shop_profile(Base):
    __tablename__ = 'shop_profile'

    sid = Column(String(20), primary_key=True)
    name = Column(String(100))
    star = Column(Integer)
    addr = Column(Integer)
    timestamp = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    def __repr__(self):
        return u'<shop_profile({}-{})>'.format(self.sid, self.name).encode('utf8')


class shop_tags(Base):
    __tablename__ = 'shop_tags'

    id = Column(Integer, Sequence('shop_tags'), primary_key=True)
    sid = Column(String(20))
    tag = Column(String(100))
    timestamp = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))

    def __repr__(self):
        return u'<shop_tags({}-{})>'.format(self.sid, self.tag).encode('utf8')


def install(conn='sqlite:///database.sqlite3'):
    global engine
    engine = create_engine(conn)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


if __name__ == '__main__':
    Session = install('sqlite:///test.sqlite3')
    session = Session()
    session.add(shop_profile(sid='111', name=u'测试名称', star='40', addr=u'陕西西安'))

    many = [
        shop_profile(sid='211', name=u'批量名称1', star='31', addr=u'陕西1西安'),
        shop_profile(sid='222', name=u'批量名称2', star='32', addr=u'陕西2西安'),
        shop_profile(sid='233', name=u'批量名称3', star='33', addr=u'陕西3西安'),
        ]
    session.add_all(many)
    session.commit()
