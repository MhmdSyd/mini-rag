from .BaseDataModel import BaseDataModel
from .db_schemes import DataChunk
from .enums.DataBaseEnum import DataBaseEnum
from bson.objectid import ObjectId
from pymongo import InsertOne

class ChunkModel(BaseDataModel):

    def __init__(self,db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]

    @classmethod
    async def create_instance(cls,db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance
    
    async def init_collection(self):
        all_collection = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_CHUNK_NAME.value not in all_collection:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_CHUNK_NAME.value]
            indexes = ChunkModel.get_indexes()
            for indx in indexes:
                await self.collection.create_index(
                    indx['key'],
                    name=indx['name'],
                    unique=indx['unique'],
                )
    
    async def create_chunk(self, chunk: DataChunk):
        result = await self.collection.insert_one(chunk.dict(by_alias=True, exclude_unset=True))
        chunk._id = result.inserted_id
        return chunk
    
    async def get_chunk(self, chunk_id: str):

        record = await self.collection.find_one({
            "_id": ObjectId(chunk_id)
        })

        if record is None:

            return None

        return DataChunk(**record)
    
    async def insert_many_chunks(self, chunks: list, batch_size: int=100):

        for indx in range(0, len(chunks), batch_size):
            batch = chunks[indx:indx+batch_size]

            operations = [
                InsertOne(chunk.dict(by_alias=True, exclude_unset=True))
                for chunk in batch
            ]

            await self.collection.bulk_write(operations)

        return len(chunks)
    
    async def delete_project_chunks(self, project_id: ObjectId):
        result = await self.collection.delete_many({
            "chunk_project_id": project_id
        })

        return result.deleted_count

    @classmethod
    def get_indexes(cls):
        return [
            {
                'key': [
                    ("chunk_project_id", 1),
                ],
                'name': 'chunk_project_id_index_1',
                'unique': False
            }

        ]

