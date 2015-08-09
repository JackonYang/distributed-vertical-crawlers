# -*- Encoding: utf-8 -*-
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, TIMESTAMP
from sqlalchemy import text, Sequence

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()
engine = None


class BaseModel(Base):
    __abstract__ = True

    create_time = Column(TIMESTAMP, server_default=text('CURRENT_TIMESTAMP'))


class HisCount(BaseModel):
    __abstract__ = True

    id = Column(Integer, Sequence('hiscount_id'), primary_key=True)
    key = Column(String(20))
    count = Column(Integer)

    def __init__(self, key, count):
        self.key = key
        self.count = count


class Peer(BaseModel):
    __abstract__ = True

    id = Column(Integer, Sequence('peer_id'), primary_key=True)
    key1 = Column(String(20))
    key2 = Column(String(20))

    def __init__(self, key1, key2):
        self.key1 = key1
        self.key2 = key2


def install(conn='sqlite:///db.sqlite3'):
    global engine
    engine = create_engine(conn)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


class TestCount(HisCount):
    __tablename__ = 'TestCount'


class TestPeer(Peer):
    __tablename__ = 'TestPeer'


if __name__ == '__main__':
    Session = install('sqlite:///test.sqlite3')
    session = Session()
    session.close()
