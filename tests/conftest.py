import os
import shutil
import pytest
import tempfile
from pathlib import Path
from app.scanner.scanner import scan_dir
tmp_dir = tempfile.mkdtemp()
db_path = os.path.join(tmp_dir,'test.db')
os.environ["LOCALMIND_DB"] = f"sqlite:///{db_path}"
from app.database.models import engine,Base,init_fts
from sqlalchemy import text

TEST_DIR = Path(__file__).parent / "Test"

@pytest.fixture(autouse=True, scope='function')
def clean_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with engine.begin() as conn:
        stmt = text("DROP TABLE IF EXISTS content_fts")
        conn.execute(stmt)
        stmt = text("DROP TABLE IF EXISTS content_fts_cn")
        conn.execute(stmt)
    init_fts(engine)
@pytest.fixture
def seeded_db(tmp_path,clean_db):
    scan_dir(TEST_DIR)
def pytest_sessionfinish(session, exitstatus):
    shutil.rmtree(tmp_dir,ignore_errors=True)