from pathlib import Path
from .base import BaseParser
from .md import MarkdownParser
from .code import CodeParser

class UnsupportedFormatError(Exception):
    pass

markdown_parser = MarkdownParser()
code_parser = CodeParser()

REGISTRY = {
    "txt" : markdown_parser,
    "md" : markdown_parser,

    "py": code_parser,
    "java": code_parser,
    "c": code_parser,
    "cpp": code_parser,
    "h": code_parser,
    "hpp": code_parser,
    "js": code_parser,
    "ts": code_parser,
    "jsx": code_parser,
    "tsx": code_parser,
    "go": code_parser,
    "rs": code_parser,
    "rb": code_parser,
    "php": code_parser,
    "swift": code_parser,
    "kt": code_parser,
    "scala": code_parser,
    "sh": code_parser,
    "bash": code_parser,
    "zsh": code_parser,
    "sql": code_parser,
    "html": code_parser,
    "css": code_parser,
    "scss": code_parser,
    "less": code_parser,
    "json": code_parser,
    "xml": code_parser,
    "yaml": code_parser,
    "yml": code_parser,
    "toml": code_parser,
    "ini": code_parser,
    "conf": code_parser
}

def parse_file(path):
    path = Path(path)
    suffix = path.suffix.lower().removeprefix('.')
    parser = REGISTRY.get(suffix)
    if parser is None:
        raise UnsupportedFormatError(f"[ERROR]:Unsupported file format: {path.suffix or 'no suffix'}\nfile: {path}")
    return parser.parse(path)