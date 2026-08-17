from watchdog.events import FileSystemEventHandler
from pathlib import Path
from app.database.models import File, engine
from app.scanner.scanner import calculate_hash,process_one_file
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy import select,text

Session = sessionmaker(bind=engine)

class FileChangeHandler(FileSystemEventHandler):
    def _handle_file(self, path,event_type):
        with Session() as session:
            result = process_one_file(path, session)
            session.commit()
            if result == "updated":
                print(f"[INFO]:file {path} {event_type} and indexed")
            elif result == "skipped":
                print(f"[INFO]:file {path} {event_type} but content unchanged (skipped)")
            else:
                print(f"[INFO]:failed to progress {path}")

    def on_created(self, event):
        self._handle_file(event.src_path,"created")

    def on_deleted(self, event):
        file_path = Path(event.src_path)
        with Session() as session:
            stmt=select(File).where(File.path == str(file_path.absolute()))
            file_obj = session.execute(stmt).scalar_one_or_none()
            if file_obj:
                session.delete(file_obj)
                session.commit()
                print(f"[INFO]:file {file_path} deleted and removed from index")
            else:
                print(f"[ERROR]:file {file_path} not found in database")

    def on_modified(self, event):
        self._handle_file(event.src_path,"modified")

    def on_moved(self, event):
        old_path = str(Path(event.src_path).absolute())
        new_path = Path(event.dest_path).resolve()

        if not new_path.is_file():
            return

        with Session() as session:
            try:
                stmt = select(File).where(File.path == old_path)
                file_record = session.execute(stmt).scalar_one_or_none()
                if file_record:
                    file_record.path = str(new_path)
                    file_record.name = new_path.name
                    file_record.extension = new_path.suffix
                    try:
                        stat_obj = new_path.stat()
                        file_record.size = stat_obj.st_size
                        file_record.mtime = datetime.fromtimestamp(stat_obj.st_mtime)
                        file_hash = calculate_hash(new_path, buffer_size=65536)
                        if file_hash:
                            file_record.hash = file_hash
                    except Exception as e:
                        print(f"[ERROR]:failed to update metadata for moved file: {e}")
                        session.rollback()
                        return
                    result = process_one_file(new_path, session)
                    session.commit()
                    if result == "updated":
                        print(f"[INFO]:file moved from {old_path} to {new_path} and re-indexed")
                    elif result == "skipped":
                        print(f"[INFO]:file moved from {old_path} to {new_path} (content unchanged)")
                    else:
                        print(f"[INFO]:failed to progress moved file: {new_path}")
                else:
                    print(f"[ERROR]:file {old_path} not found in database, treating as new file")
                    result = process_one_file(new_path, session)
                    session.commit()
                    if result == "updated":
                        print(f"[INFO]:new file detected after move: {new_path}")

            except PermissionError:
                print(f"[ERROR]:No permission to access the path :{old_path}")
            except Exception as e:
                print(f"[ERROR]:Progress file {old_path} failed:{e}")