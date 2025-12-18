from pathlib import Path
from llama_index.readers.file import PyMuPDFReader
from llama_index.core import Document


def load_pdf(path: str) -> list[Document]:
    loader = PyMuPDFReader()
    pages = loader.load(file_path=Path(path))
    text = "\n\n".join([p.get_content() for p in pages])
    return [Document(text=text)]
