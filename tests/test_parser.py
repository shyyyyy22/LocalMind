import pytest
from app.scanner.scanner import scan_dir
from app.search import search
from app.database.models import engine, FileContent
from app.parser import parse_file, UnsupportedFormatError
from sqlalchemy.orm import sessionmaker
from sqlalchemy import func
from conftest import TEST_DIR

Session = sessionmaker(bind=engine)

def test_md(tmp_path):
    text ="---\ntitle: 测试文档\ntags: [测试, frontmatter]\n---\n# 正文标题\n这里是正文独有的一句话"
    (tmp_path / "md_test.md").write_text(text, encoding='utf8')
    result = parse_file(tmp_path / "md_test.md")
    assert 'frontmatter' not in result
    assert '这里是正文独有的一句话' in result

def test_txt_and_py(seeded_db):
    contents = []
    result1 = search.search_by_ext('py')
    result2 = search.search_by_ext('txt')
    result1 = [f for f in result1 if f.size > 0]
    result2 = [f for f in result2 if f.size > 0]
    paths = [f.path for f in result1 + result2]
    for path in paths:
        contents.append(parse_file(path))
    for content in contents:
        assert content != ''
def test_without_ext(seeded_db):
    with pytest.raises(UnsupportedFormatError):
        paths = [f.path for f in search.search_by_ext('')]
        assert paths
        for path in paths:
            parse_file(path)
def test_gbk_file(tmp_path):
    text = "这是GBK编码的中文测试内容"
    (tmp_path / "gbk_test.txt").write_text(text, encoding='gbk')
    assert parse_file(tmp_path / "gbk_test.txt") == text
def test_null_file(seeded_db):
    path = TEST_DIR / "special" / "空文件.txt"
    content = parse_file(path)
    assert content == ''
def test_status(tmp_path):
    good = (tmp_path / "good.txt").write_text('good file',encoding='utf8')
    no_ext = (tmp_path / "no_ext").write_text('unsupported file', encoding='utf8')
    bad = (tmp_path / "bad.txt").write_bytes(b'\xff\xfe\xfa\x00\x80')
    scan_dir(tmp_path)
    with Session() as session:
        count = session.query(FileContent).count()
        assert count == 3
        status_counts = (session.query(FileContent.status,func.count()).group_by(FileContent.status).all())
        status_dict = {status: cnt for status,cnt in status_counts}
        assert status_dict == {'success': 1, 'unsupported': 1, 'error': 1}