from datetime import datetime
from sqlalchemy import create_engine,Column,String,Integer,DateTime,BigInteger,Text,Enum,ForeignKey,text
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
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
Session = sessionmaker(bind=engine)

def init_fts(engine):
    with engine.begin() as conn:
        conn.execute(text("""CREATE VIRTUAL TABLE IF NOT EXISTS content_fts USING fts5
                          (content,
                          content = file_contents,
                          content_rowid = id,
                          tokenize='unicode61'
                          )
                      """))
        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS content_fts_after_insert AFTER INSERT ON file_contents
            BEGIN
                INSERT INTO content_fts(rowid, content) VALUES (new.id, new.content);
            END;
        """))
        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS content_fts_after_update AFTER UPDATE OF content ON file_contents
            BEGIN
                INSERT INTO content_fts(content_fts, rowid, content) VALUES ('delete', old.id, old.content);
                INSERT INTO content_fts(rowid, content) VALUES (new.id, new.content);
            END;
        """))
        conn.execute(text("""
            CREATE TRIGGER IF NOT EXISTS content_fts_after_delete AFTER DELETE ON file_contents
            BEGIN
                DELETE FROM content_fts WHERE rowid=old.id;
            END;
        """))