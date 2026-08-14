import pytest
from app.search import search
from conftest import seeded_db

def test_name_fuzzy_search(seeded_db):
    results1 = search.search_by_name("transformer")
    results2 = search.search_by_name("笔记")
    assert len(results1) == 2 and len(results2) == 1
def test_search_by_ext(seeded_db):
    results1 = search.search_by_ext(".py")
    results2 = search.search_by_ext("py")
    results3 = search.search_by_ext("")
    file_names=[f.name for f in results3]
    assert sorted(file_names) == sorted(['.hidden_file', 'no_extension'])
    assert len(results1) == 4
    assert len(results2) == 4
def test_search_by_path(seeded_db):
    results1 = search.search_by_path(r"Test\code")
    results2 = search.search_by_path(r"Test/code")
    assert len(results1) == len(results2)
    assert len(results1) == 6
    assert len(results2) == 6
def test_search_by_size(seeded_db):
    results1 = search.search_by_size(size_max=0)
    results2 = search.search_by_size(size_min=1000)
    assert len(results1) == 1 and len(results2) == 7
def test_search_by_vaild_mtime(seeded_db):
    results1 = search.search_by_mtime(mtime_start="2026-08-01-00")
    assert len(results1) == 27
def test_search_by_invalid_mtime(seeded_db):
    with pytest.raises(ValueError):
        search.search_by_mtime(mtime_start="2026/8/1/00")
def test_combined_search_with_limit(seeded_db):
    results1=search.search(ext='py',size_min=100,limit_num=2)
    assert len(results1) == 2
