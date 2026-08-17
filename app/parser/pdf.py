from . import NoTextError
from .base import BaseParser
from pypdf import PdfReader

class PdfParser(BaseParser):
    def parse(self, path):
        reader = PdfReader(path)
        pages=reader.pages
        content=''
        texts = []
        texts.extend(page.extract_text() for page in pages)
        content += "\n".join(text for text in texts if text != '')
        if content == '':
            raise NoTextError(f"[ERROR]: {path} is a scanned pdf file or blank")
        return content