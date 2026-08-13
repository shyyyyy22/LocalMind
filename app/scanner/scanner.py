import hashlib
from pathlib import Path
from sqlalchemy.orm import sessionmaker
from app.database.models import File,engine
from datetime import datetime

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
    with Session() as session:
        for file_path in root.rglob('*'):
            if not file_path.is_file():
                continue
            else:
                try:
                    stat_obj = file_path.stat()
                    file_hash = calculate_hash(file_path, buffer_size=65536)
                    if file_hash is None:
                        continue
                    else:
                        session.merge(File(path=str(file_path.absolute()),
                                           name=str(file_path.name),
                                           extension=str(file_path.suffix),
                                           mtime=datetime.fromtimestamp(stat_obj.st_mtime),
                                           ctime=datetime.fromtimestamp(stat_obj.st_ctime),
                                           size=stat_obj.st_size,
                                           hash=file_hash))
                        count += 1
                    if(count % 50 == 0):
                        session.commit()
                        print(f"[INFO]:{count} files scanned")
                except PermissionError:
                    print(f"[ERROR]:No permission to access the path :{file_path}")
                    continue
                except Exception as e:
                    print(f"[ERROR]:Progress file {file_path} failed:{e}")
                    continue
        session.commit()
        print(f"[INFO]:Successful! {count} files scanned")

if __name__ == '__main__':
    filepath = r"D:\freshman_2\数字系统设计基础"
    scan_dir(filepath)