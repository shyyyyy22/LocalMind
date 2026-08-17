from watchdog.events import FileCreatedEvent, FileModifiedEvent, FileDeletedEvent, FileMovedEvent
from app.database.models import engine, File, FileContent
from app.scanner.scanner import scan_dir,process_one_file
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.scanner.watcher import FileChangeHandler

Session = sessionmaker(bind=engine)

def test_scanner_hash(tmp_path):
    file_path = tmp_path / 'test.txt'
    file_path.write_text('hello world',encoding='utf8')

    with Session() as session:
        result1 = process_one_file(file_path,session)
        assert result1 == 'updated'

        file_path.write_text('hello sea',encoding='utf8')

        result2 = process_one_file(file_path,session)
        assert result2 == 'updated'

        result3 = process_one_file(file_path,session)
        assert result3 == 'skipped'

        files = session.query(File).all()
        assert len(files) == 1
        content_records = session.query(FileContent).all()
        assert len(content_records) == 1
        assert content_records[0].content == 'hello sea'

        rows = session.execute(text("SELECT content FROM content_fts WHERE rowid = :rid"),{'rid':content_records[0].id}).fetchall()
        assert len(rows) == 1
        assert rows[0][0] == 'hello sea'
def test_scan_deletion(tmp_path):
    file_path = tmp_path / 'delete.txt'
    file_path.write_text('hello world',encoding='utf8')
    scan_dir(tmp_path)

    with Session() as session:
        file_record = session.query(File).filter_by(path = str(file_path.absolute())).first()
        assert file_record is not None
        content_record = session.query(FileContent).filter_by(id=file_record.id).first()
        assert content_record is not None
        fts_row = session.execute(text("SELECT rowid FROM content_fts WHERE rowid = :rid"),{'rid':file_record.id}).fetchone()
        assert fts_row is not None

        file_path.unlink()
        scan_dir(tmp_path)

        file_record = session.query(File).filter_by(path=str(file_path.absolute())).first()
        assert file_record is None
        all_fts = session.execute(text("SELECT rowid FROM content_fts")).fetchall()
        assert len(all_fts) == 0
def test_watcher_created(tmp_path):
    handler = FileChangeHandler()
    file_path = tmp_path / 'create.txt'
    file_path.write_text('create content',encoding='utf8')
    event = FileCreatedEvent(str(file_path.absolute()))
    handler.on_created(event)

    with Session() as session:
        file = session.query(File).filter_by(path=str(file_path.absolute())).first()
        assert file is not None
        assert file.name == "create.txt"
        content = session.query(FileContent).filter_by(id=file.id).first()
        assert content is not None
        assert content.content == 'create content'
        fts = session.execute(text("SELECT content FROM content_fts WHERE rowid = :rid"),
                                  {'rid': file.id}).fetchone()
        assert fts is not None
        assert fts[0] == 'create content'
def test_watcher_modified(tmp_path):
    file_path = tmp_path / 'modified.txt'
    file_path.write_text('original',encoding='utf8')
    scan_dir(tmp_path)
    with Session() as session:
        record = session.query(File).filter_by(path=str(file_path.absolute())).first()
        old_id= record.id
    file_path.write_text('modified',encoding='utf8')
    handler = FileChangeHandler()
    event = FileModifiedEvent(str(file_path.absolute()))
    handler.on_modified(event)

    with Session() as session:
        session.expire_all()
        updated_record = session.query(File).filter_by(path=str(file_path.absolute())).first()
        assert updated_record.id == old_id
        updated_content = session.query(FileContent).filter_by(id=updated_record.id).first()
        assert updated_content.content == 'modified'

        fts = session.execute(text("SELECT content FROM content_fts WHERE rowid = :rid"),{'rid': updated_record.id}).fetchone()
        assert fts[0] == 'modified'

        rows_new = session.execute(text("SELECT rowid FROM content_fts WHERE content MATCH 'modified'")).fetchall()
        assert len(rows_new) == 1
        rows_old = session.execute(text("SELECT rowid FROM content_fts WHERE content MATCH 'original'")).fetchall()
        assert len(rows_old) == 0
def test_watcher_deleted(tmp_path):
    file_path = tmp_path / 'deleted.txt'
    file_path.write_text('deleted',encoding='utf8')
    scan_dir(tmp_path)
    with Session() as session:
        record = session.query(File).filter_by(path=str(file_path.absolute())).first()
        assert record is not None
    file_path.unlink()
    handler = FileChangeHandler()
    event = FileDeletedEvent(str(file_path.absolute()))
    handler.on_deleted(event)

    with Session() as session:
        record = session.query(File).filter_by(path=str(file_path.absolute())).first()
        assert record is None

        fts = session.execute(text("SELECT rowid FROM content_fts")).fetchall()
        assert len(fts) == 0
def test_watcher_moved(tmp_path):
    src = tmp_path / 'source.txt'
    src.write_text('moved',encoding='utf8')
    scan_dir(tmp_path)
    with Session() as session:
        original_record = session.query(File).filter_by(path=str(src.absolute())).first()
        assert original_record is not None

    dest = tmp_path / 'dest.txt'
    src.rename(dest)
    event = FileMovedEvent(str(src.absolute()),str(dest.absolute()))
    handler = FileChangeHandler()
    handler.on_moved(event)

    with Session() as session:
        record = session.query(File).filter_by(path=str(dest.absolute())).first()
        assert record is not None
        assert record.id == original_record.id

        content = session.query(FileContent).filter_by(id=record.id).first()
        assert content.content == 'moved'

        fts = session.execute(text("SELECT content FROM content_fts WHERE rowid = :rid"),{'rid': record.id}).fetchone()
        assert fts[0] == 'moved'

        old_record = session.query(File).filter_by(path=str(src.absolute())).first()
        assert old_record is None