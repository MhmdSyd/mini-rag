from .BaseController import BaseController
from .ProjectController import ProjectController
from models import ProcessEnums

from langchain_community.document_loaders import TextLoader, PyMuPDFLoader
from dataclasses import dataclass
from typing import List
import os

from langchain.text_splitter import RecursiveCharacterTextSplitter

@dataclass
class Document:
    page_content: str
    metadata: dict

class ProcessController(BaseController):

    def __init__(self, project_id: str):
        super().__init__()

        self.project_id = project_id
        self.project_path = ProjectController().get_project_path(project_id=project_id)


    def get_file_extension(self, file_id: str):

        return os.path.splitext(file_id)[-1]

    def get_file_loader(self, file_id: str):

        file_ext = self.get_file_extension(file_id=file_id)

        file_path = os.path.join(
            self.project_path,
            file_id
        )

        if file_ext == ProcessEnums.TXT.value:
            return TextLoader(file_path, encoding='utf-8')

        elif file_ext == ProcessEnums.PDF.value:
            return PyMuPDFLoader(file_path=file_path)

        else:
            return None

    def get_file_content(self, file_id: str):

        loader = self.get_file_loader(file_id=file_id)
        return loader.load()

    def process_file_content(self, file_content: list, file_id: str,
                            chunk_size: int=200, overlap_size: int=20):

        file_content_texts = []
        file_content_metadata = []


        for page in file_content:
            file_content_texts.append(page.page_content)
            file_content_metadata.append(page.metadata)

        chunks = self.process_simpler_splitter(
            texts=file_content_texts,
            metadatas=file_content_metadata,
            chunk_size=chunk_size
        )
        
        return chunks
    

    def process_simpler_splitter(self, texts:List[str], metadatas: List[str], chunk_size: int, splitter_tag: str="\n\n"):

        chunks = []
        for text, metadata in zip(texts, metadatas):

            if len(text) > chunk_size:
                
                _ = [
                        chunks.append(Document(
                            page_content=current_chunk.strip(),
                            metadata=metadata
                        )) for current_chunk in text.split(splitter_tag) if current_chunk.strip()
                    ]
            else:
                chunks.append(Document(
                    page_content=text.strip(),
                    metadata=metadata
                ))


        return chunks




