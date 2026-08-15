from datetime import datetime
from sqlalchemy import create_engine,Column,String,Integer,DateTime,BigInteger,Text,Enum,ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from app.core.config import DB_PATH

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
    content = relationship("FileContent",back_populates="file",uselist=False,cascade="all,delete-orphan")

class FileContent(Base):
    __tablename__ = 'file_contents'
    id = Column(Integer,ForeignKey("files.id",ondelete="CASCADE"),primary_key=True)
    content = Column(Text)
    status =  Column(Enum("success","error","unsupported"))
    indexed_at = Column(DateTime,default=datetime.now())
    file = relationship("File",back_populates="content")

engine = create_engine(DB_PATH,echo=False)
Base.metadata.create_all(engine)
