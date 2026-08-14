import os
import shutil
import pytest
import tempfile
from pathlib import Path
from app.scanner.scanner import scan_dir
tmp_dir = tempfile.mkdtemp()
db_path = os.path.join(tmp_dir,'test.db')
os.environ["LOCALMIND_DB"] = f"sqlite:///{db_path}"
from app.database.models import engine,Base
TEST_DIR = Path(__file__).parent / "Test"

@pytest.fixture(autouse=True, scope='function')
def clean_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
@pytest.fixture
def seeded_db(clean_db):
    scan_dir(TEST_DIR)
def pytest_sessionfinish(session, exitstatus):
    shutil.rmtree(tmp_dir,ignore_errors=True)