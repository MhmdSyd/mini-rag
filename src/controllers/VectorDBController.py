from .BaseController import BaseController  
from models.db_schemes import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum
from typing import List

class VectorDBController(BaseController):

    def __init__(self, vectordb_client, generation_client, embedding_client):
        super().__init__()

        self.vectordb_client = vectordb_client
        self.generation_client = generation_client  
        self.embedding_client = embedding_client

    def create_collection_name(self, project_id: str):
        return f"collection_{project_id}".strip()
    
    def reset_vectordb_collection(self, project: Project):
        collection_name = self.create_collection_name(project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)
    
    def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)

        return collection_info
    
    def index_into_vectordb(self, project: Project, chunks: List[DataChunk],
                            chunks_ids: List[int],
                            do_reset: bool = False):
        # 1. get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)

        # 2. manage items
        texts = [ c.chunk_text for c in chunks ]
        metadata = [ c.chunk_metadata for c in  chunks]
        vectors = [
            self.embedding_client.embed_text(text=text, 
                                             document_type=DocumentTypeEnum.DOCUMENT.value)
            for text in texts
        ]


        # 3. create collection if not exists
        _ = self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size=self.embedding_client.embedding_size,
            do_reset=do_reset,
        )

        # 4. insert into vector db
        _ = self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadata=metadata,
            vectors=vectors,
            record_ids=chunks_ids,
        )

        return True
    