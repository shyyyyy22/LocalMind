from pathlib import Path
from .base import BaseParser

class CodeParser(BaseParser):
    def parse(self, path):
        path = Path(path)
        return BaseParser.read_file(path)