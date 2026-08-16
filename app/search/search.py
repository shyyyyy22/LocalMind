from app.database.models import File, engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from sqlalchemy import select,text

Session = sessionmaker(bind=engine)
def search(name=None, ext=None, path=None, size_min=None, size_max=None,
           mtime_start=None, mtime_end=None, content=None, limit_num=50):
    """按元数据条件组合搜索文件，所有条件为 None 时表示不过滤。

    Args:
        name: 文件名关键词，模糊匹配（如 "transformer" 可匹配 "transformer.py"）。
        ext: 扩展名，带不带点均可（"pdf" 和 ".pdf" 等价）。
        path: 路径关键词，模糊匹配（如 "D:/学习"）。
        size_min: 最小文件大小（字节），None 表示无下界。
        size_max: 最大文件大小（字节），None 表示无上界。
        mtime_start: 修改时间起点，格式 "YYYY-MM-DD-HH"，条件为 >=（含该小时起点）。
        mtime_end: 修改时间终点，格式 "YYYY-MM-DD-HH"，条件为 <（不含该小时起点）。
        content: 文件包含内容
        limit_num: 最多返回条数，默认 50。

    Returns:
        list[File]: 按文件名升序排列的 File 对象列表。

    Raises:
        ValueError: mtime_start 或 mtime_end 格式非法时。
    """

    conditions=[]
    if name is not None:
        conditions.append(File.name.like(f"%{name}%"))
    if ext is not None:
        if ext !="":
            if ext[0] != ".":
                ext="." + ext
        conditions.append(File.extension == ext)
    if path is not None:
        path=path.replace("/", "\\")
        conditions.append(File.path.like(f"%{path}%"))
    if size_min is not None:
        conditions.append(File.size >= size_min)
    if size_max is not None:
        conditions.append(File.size <= size_max)
    if mtime_start is not None:
        try:
            start_time = datetime.strptime(mtime_start, "%Y-%m-%d-%H")
        except ValueError as e:
            raise ValueError("[ERROR]:mtime_start format error: should be YYYY-MM-DD-HH") from e
        conditions.append(File.mtime >= start_time)
    if mtime_end is not None:
        try:
            end_time = datetime.strptime(mtime_end, "%Y-%m-%d-%H")
        except ValueError as e:
            raise ValueError(f"[ERROR]:mtime_end format error: should be YYYY-MM-DD-HH") from e
        conditions.append(File.mtime < end_time)
    fts_rowids=[]
    if content is not None:
        query = content
        stmt=text("SELECT rowid FROM content_fts WHERE content MATCH :query ORDER BY bm25(content_fts) ASC LIMIT :limit",)
        with engine.connect() as conn:
            try:
                results = conn.execute(stmt,{"query":query,"limit":limit_num})
                fts_rowids = [row.rowid for row in results]
                if fts_rowids:
                    conditions.append(File.id.in_(fts_rowids))
            except Exception as e:
                raise ValueError(f"[ERROR]:content search failed:{e}") from e

    stmt = select(File).where(*conditions).order_by(File.name).limit(limit_num)
    with Session() as session:
        results = session.execute(stmt).scalars().all()

    if fts_rowids:
        id_to_file = {f.id: f for f in results}
        ordered_result =[id_to_file[id] for id in fts_rowids if id in id_to_file]
        return ordered_result

    return results

def search_by_name(name,limit_num=50):
    return search(name=name, limit_num=limit_num)
def search_by_ext(ext, limit_num=50):
    return search(ext=ext, limit_num=limit_num)
def search_by_path(path, limit_num=50):
    return search(path=path, limit_num=limit_num)
def search_by_size(size_min=None, size_max=None,limit_num=50):
    return search(size_min=size_min, size_max=size_max, limit_num=limit_num)
def search_by_mtime(mtime_start=None, mtime_end=None, limit_num=50):
    return search(mtime_start=mtime_start, mtime_end=mtime_end, limit_num=limit_num)
def search_by_content(content, limit_num=50):
    return search(content=content, limit_num=limit_num)

if __name__ == "__main__":
    print(search_by_path("Test\code"))
