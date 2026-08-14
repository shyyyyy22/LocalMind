from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from pathlib import Path
from app.database.models import File, engine
from app.scanner.scanner import calculate_hash
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy import select

Session = sessionmaker(bind=engine)

class FileChangeHandler(FileSystemEventHandler):
    def process_file(self,file_path:Path):
        if file_path.is_file():
            with Session() as session:
                try:
                    stat_obj = file_path.stat()
                    file_hash = calculate_hash(file_path, buffer_size=65536)
                    if file_hash is None:
                        return False
                    stmt = select(File).where(File.path == str(file_path.absolute()))
                    file_record = session.execute(stmt).scalar_one_or_none()
                    if file_record:
                        file_record.name = file_path.name
                        file_record.extension = file_path.suffix
                        file_record.size = stat_obj.st_size
                        file_record.mtime = datetime.fromtimestamp(stat_obj.st_mtime)
                        file_record.hash = file_hash
                        print(f"[INFO]:File {file_path} modified")
                    else:
                        session.add(File(path=str(file_path.absolute()),
                                         name=str(file_path.name),
                                         extension=str(file_path.suffix),
                                         mtime=datetime.fromtimestamp(stat_obj.st_mtime),
                                         ctime=datetime.fromtimestamp(stat_obj.st_ctime),
                                         size=stat_obj.st_size,
                                         hash=file_hash))
                        print(f"[INFO]:File {file_path} created")
                    session.commit()
                except PermissionError:
                    print(f"[ERROR]:No permission to access the path :{file_path}")
                except Exception as e:
                    print(f"[ERROR]:Progress file {file_path} failed:{e}")

        else:
            return False
    def on_created(self, event):
        self.process_file(Path(event.src_path))

    def on_deleted(self, event):
        file_path = Path(event.src_path)
        with Session() as session:
            stmt=select(File).where(File.path == str(file_path.absolute()))
            file_obj = session.execute(stmt).scalar_one_or_none()
            if file_obj:
                session.delete(file_obj)
                session.commit()
                print(f"[INFO]:File {file_path} deleted")
            else:
                print(f"[ERROR]:File {file_path} does not exist")

    def on_modified(self, event):
        self.process_file(Path(event.src_path))

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
                    stat_obj = new_path.stat()

                    file_record.path = str(new_path)
                    file_record.name = new_path.name
                    file_record.extension = new_path.suffix
                    file_record.size = stat_obj.st_size
                    file_record.mtime = datetime.fromtimestamp(stat_obj.st_mtime)
                    file_hash = calculate_hash(new_path, buffer_size=65536)
                    if file_hash:
                        file_record.hash = file_hash
                    session.commit()

                    print(f"[INFO]:File moved: {old_path} -> {new_path}")
                else:
                    print(f"[WARNING]:Original file does not exist: {old_path}")
            except PermissionError:
                print(f"[ERROR]:No permission to access the path :{old_path}")
            except Exception as e:
                print(f"[ERROR]:Progress file {old_path} failed:{e}")


if __name__ == '__main__':
    observer = Observer()
    handler = FileChangeHandler()
    observer.schedule(handler, r"D:\Py_Project\LocalMind\tests\Test", recursive=True)
    observer.start()
    try:
        observer.join()
    except KeyboardInterrupt:
        observer.stop()
    observer.join()