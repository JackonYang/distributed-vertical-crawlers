# -*- Encoding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy import Sequence


Base = declarative_base()


class download_job(Base):
    __tablename__ = 'download_job'

    id = Column(Integer, Sequence('job_id_seq'), primary_key=True)
    url = Column(String(500))
    filename = Column(String(100))
    status = Column(String(10))

    def __repr__(self):
        return self.url


if __name__ == '__main__':
    engine = create_engine('sqlite:///database.sqlite3', echo=True)
    Base.metadata.create_all(engine) 
