import os
from sqlalchemy import create_engine,Column,String,Integer,DateTime,BigInteger
from sqlalchemy.orm import declarative_base

Base=declarative_base()
class File(Base):
    __tablename__ = 'files'
    id = Column(Integer,primary_key=True)
    path = Column(String(512),unique=True)
    name = Column(String(256))
    extension = Column(String(32))
    size = Column(BigInteger)
    ctime = Column(DateTime)
    mtime = Column(DateTime)
    hash = Column(String(64))

engine = create_engine(os.getenv("LOCALMIND_DB",'sqlite:///localmind.db'),echo=False)
Base.metadata.create_all(engine)
