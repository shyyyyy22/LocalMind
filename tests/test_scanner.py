import os
from conftest import TEST_DIR
from app.database.models import engine,File
from app.scanner.scanner import scan_dir
from sqlalchemy import select,func
from sqlalchemy.orm import sessionmaker

Session = sessionmaker(bind=engine)

EXPECTED_TOTAL_COUNT = 30

def test_scan_dir():
    scan_dir(TEST_DIR)
    with Session() as session:
        count = session.execute(select(func.count()).select_from(File)).scalar()
    assert count == EXPECTED_TOTAL_COUNT
def test_scan_idempotent():
    scan_dir(TEST_DIR)
    with Session() as session:
        count1 = session.execute(select(func.count()).select_from(File)).scalar()
        scan_dir(TEST_DIR)
        count2 = session.execute(select(func.count()).select_from(File)).scalar()
    assert count1 == EXPECTED_TOTAL_COUNT
    assert count2 == EXPECTED_TOTAL_COUNT
    assert count1 == count2
def test_hash():
    scan_dir(TEST_DIR)
    with Session() as session:
        stmt=select(File).where(File.path.like(f"%空文件.txt%"))
        result = session.execute(stmt).scalar()
        assert result.hash == 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
def test_fields():
    scan_dir(TEST_DIR)
    test_path = TEST_DIR / "data/users.json"
    with Session() as session:
        stmt = select(File).where(File.path.like(f"%users.json%"))
        result = session.execute(stmt).scalar()
        real_name = os.path.basename(test_path)
        real_ext = os.path.splitext(test_path)[1]
        real_size = os.path.getsize(test_path)

        assert result.name == real_name
        assert result.extension == real_ext
        assert result.size == real_size