import argparse
from watchdog.observers import Observer
from app.search.search import search
from app.scanner.scanner import scan_dir
from app.scanner.watcher import FileChangeHandler

def truncate_middle(text,width):
    if len(text)>width:
        text=text[:width * 4 // 10] + "..." + text[len(text)-(width - 3 - width * 4 // 10):len(text)]
    return text

parser = argparse.ArgumentParser()
subparsers = parser.add_subparsers(title='subcommands',dest='command',help='sub-command help')
#search
search_parser = subparsers.add_parser('search',help='Search files')
search_parser.add_argument('--name',type=str,help='Name of file',default=None)
search_parser.add_argument('--ext',type=str,help='Extension of file',default=None)
search_parser.add_argument('--noext',action='store_true',help='match files without extension')
search_parser.add_argument('--path',type=str,help='Path of file',default=None)
search_parser.add_argument('--min_size',type=int,help='Min size of file',default=None)
search_parser.add_argument('--max_size',type=int,help='Max size of file',default=None)
search_parser.add_argument('--mtime_start',type=str,help='Start modified time of file',default=None)
search_parser.add_argument('--mtime_end',type=str,help='End modified time of file',default=None)
search_parser.add_argument('--limit',type=int,help='limit number of results',default=50)
#scanner
scan_parser = subparsers.add_parser('scan',help='Scan files')
scan_parser.add_argument('--path',type=str,help='Path of file',default=None)
#watcher
watch_parser = subparsers.add_parser('watch',help='Watch files')
watch_parser.add_argument('--path',type=str,help='Path of file',default=None)

args = parser.parse_args()
if args.command == 'search':
    try:
        ext = '' if args.noext else args.ext
        results = search(name=args.name,ext=ext,path=args.path,size_min=args.min_size,size_max=args.max_size,
                         mtime_start=args.mtime_start,mtime_end=args.mtime_end,limit_num=args.limit)
    except ValueError as e :
        parser.error(str(e))
    if results:
        print(f"[INFO]:There are total {len(results)} results")
        print("|"f"{'File_name':^30}""|"f"{'Path':^42}""|"f"{'Size':^10}""|"f"{'Modified_time':^20}""|")
        for result in results:
            unit='B'
            size=result.size
            if size>1024:
                size=size/1024
                unit='KB'
            if size>1024:
                size=size/1024
                unit='MB'
            if size>1024:
                size=size/1024
                unit='GB'
            print("|"f"{truncate_middle(result.name,30):<30}""|"f"{truncate_middle(result.path,40):<42}""|"f"{size:<7.2f} {unit:>2}""|"f"{result.mtime.strftime("%Y-%m-%d %H:%M"):^20}""|")
    else:
        print("[INFO]:There are no results")
if args.command == 'scan':
    if args.path is not None:
        scan_dir(args.path)
    else:
        print("[INFO]:No path")
if args.command == 'watch':
    if args.path is not None:
        print(f"[INFO]:Start watching {args.path}")
        observer = Observer()
        handler = FileChangeHandler()
        observer.schedule(handler, args.path, recursive=True)
        observer.start()
        try:
            observer.join()
        except KeyboardInterrupt:
            observer.stop()
        observer.join()
    else:
        print("[INFO]:No path")
