import argparse
from app.search.search import search

def truncate_middle(text,width):
    if len(text)>width:
        text=text[:width * 4 // 10] + "..." + text[len(text)-(width - 3 - width * 4 // 10):len(text)]
    return text

parser = argparse.ArgumentParser()
parser.add_argument('command', choices=['search'],type=str,help='Select command')
parser.add_argument('--name',type=str,help='Name of file',default=None)
parser.add_argument('--ext',type=str,help='Extension of file',default=None)
parser.add_argument('--noext',action='store_true',help='match files without extension')
parser.add_argument('--path',type=str,help='Path of file',default=None)
parser.add_argument('--min_size',type=int,help='Min size of file',default=None)
parser.add_argument('--max_size',type=int,help='Max size of file',default=None)
parser.add_argument('--mtime_start',type=str,help='Start modified time of file',default=None)
parser.add_argument('--mtime_end',type=str,help='End modified time of file',default=None)
parser.add_argument('--limit',type=int,help='limit number of results',default=50)
args = parser.parse_args()
if args.command == 'search':
    try:
        ext = '' if args.noext else args.ext
        results = search(name=args.name,ext=ext,path=args.path,size_min=args.min_size,size_max=args.max_size,
                         mtime_start=args.mtime_start,mtime_end=args.mtime_end,limit_num=args.limit)
    except ValueError as e :
        parser.error(str(e))
    if results:
        print(f"==There are total {len(results)} results==")
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
        print("==There are no results==")