from abc import ABC, abstractmethod
from pathlib import Path

class BaseParser(ABC):
    @abstractmethod
    def parse(self,path: str | Path) -> str:
        pass
    @staticmethod
    def read_file(path: Path):
        try:
            return path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            return path.read_text(encoding='gbk')