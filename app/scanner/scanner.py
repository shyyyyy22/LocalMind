import hashlib
from pathlib import Path
from pypdf.errors import WrongPasswordError
from sqlalchemy.orm import sessionmaker
from app.database.models import File,FileContent,engine,init_fts
from datetime import datetime
from sqlalchemy import select,text
from app.parser import parse_file, UnsupportedFormatError, NoTextError

Session=sessionmaker(bind=engine)

def calculate_hash(file_path,buffer_size=65536):
    try:
        h = hashlib.new('sha256')
        with open(file_path,'rb') as f:
            while True:
                chunk = f.read(buffer_size)
                if not chunk:
                    break
                h.update(chunk)

        return h.hexdigest()
    except FileNotFoundError:
        print(f"[ERROR]:File not found - {file_path}")
        return None
    except (PermissionError, OSError, IOError) as e:
        print(f"[ERROR]:Read file failed - {e}")
        return None
def process_one_file(file_path,session):
    file_path = Path(file_path)
    if not file_path.is_file():
        return 'error'
    try:
        stat_obj = file_path.stat()
        file_hash = calculate_hash(file_path, buffer_size=65536)

        if file_hash is None:
            return 'error'

        stmt = select(File).where(File.path == str(file_path.absolute()))
        file_record = session.execute(stmt).scalar_one_or_none()

        if file_record and file_record.hash == file_hash:
            return 'skipped'

        content_text = ''
        status = 'unsupported'
        try:
            content_text = parse_file(file_path)
            status = "success"
        except UnsupportedFormatError as e:
            print(e)
        except NoTextError as e:
            print(e)
        except WrongPasswordError as e:
            content_text = ''
            status = "error"
            print(f"[ERROR]:encrypted pdf file :{file_path} - {e}")
        except Exception as e:
            content_text = ''
            status = "error"
            print(e)

        if file_record:
            file_record.name = file_path.name
            file_record.extension = file_path.suffix
            file_record.size = stat_obj.st_size
            file_record.mtime = datetime.fromtimestamp(stat_obj.st_mtime)
            file_record.hash = file_hash

            if file_record.content:
                file_record.content.content = content_text
                file_record.content.status = status
                content_obj = file_record.content
            else:
                content_obj = FileContent(content=content_text, status=status)
                file_record.content = content_obj
        else:
            content_obj = FileContent(content=content_text, status=status)
            session.add(File(path=str(file_path.absolute()),
                             name=str(file_path.name),
                             extension=str(file_path.suffix),
                             mtime=datetime.fromtimestamp(stat_obj.st_mtime),
                             ctime=datetime.fromtimestamp(stat_obj.st_ctime),
                             size=stat_obj.st_size,
                             hash=file_hash,
                             content=content_obj))
        session.flush()

        return 'updated'
    except PermissionError:
        print(f"[ERROR]:No permission to access the path :{file_path}")
        session.rollback()
        return 'error'
    except Exception as e:
        print(f"[ERROR]:Progress file {file_path} failed:{e}")
        session.rollback()
        return 'error'


def scan_dir(root_path):
    print(f"[INFO]:Scanning {root_path}")
    try:
        root = Path(root_path)
        if not root.exists():
            print(f"[ERROR]:{root_path} does not exist")
            return None
    except Exception as e:
        print(f"[ERROR]:Can't read the path :{e}")
        return None
    count = 0
    skipped = 0
    disk_paths = set()
    with Session() as session:
        for file_path in root.rglob('*'):
            if not file_path.is_file():
                continue
            disk_paths.add(str(file_path.absolute()))
            result = process_one_file(file_path,session)
            if result == 'skipped':
                skipped += 1
            if result == 'updated':
                count += 1
                if count % 50 == 0:
                    session.commit()
                    print(f"[INFO]:{count} files scanned")

        session.commit()
        print(f"[INFO]:Successful! {count} files scanned, {skipped} files skipped")

        db_paths = set(session.execute(select(File.path)).scalars().all())
        missing = db_paths - disk_paths
        for path in missing:
            stmt = text("DELETE FROM file_contents WHERE id IN (SELECT id FROM files WHERE path = :path)")
            session.execute(stmt,{"path": path})
            stmt = text("DELETE FROM files WHERE path = :path")
            session.execute(stmt,{"path": path})
        session.commit()
        if missing:
            print(f"[INFO]:remove {len(missing)} files orphaned files from database")