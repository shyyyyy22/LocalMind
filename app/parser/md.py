from pathlib import Path
from .base import BaseParser

class MarkdownParser(BaseParser):
    def parse(self,path):
        path = Path(path)
        text = BaseParser.read_file(path)
        return self.strip_front_matter(text)

    @staticmethod
    def strip_front_matter(content):
        lines = content.splitlines()
        if not lines:
            return ''
        if lines[0].strip() != '---':
            return content
        end_idx = None
        for i in range(1,len(lines)):
            if lines[i].strip() == '---':
                end_idx = i
                break
        if end_idx is None:
            return content

        return "\n".join(lines[end_idx + 1:])
