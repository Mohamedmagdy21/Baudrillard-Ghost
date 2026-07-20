from src.models.db_schema.response import Response
from .BaseDataModel import BaseDataModel
from .db_schema import project
from .enums.DataBaseEnum import DataBaseEnum
from pymongo import InsertOne


class ResponseModel(BaseDataModel):

    def __init__(self, db_client: object):
        super().__init__(db_client=db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_RESPONSES_HISTORY.value]

    @classmethod
    async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance

    async def init_collection(self):
        all_collection = await self.db_client.list_collection_names()
        if DataBaseEnum.COLLECTION_RESPONSES_HISTORY.value not in all_collection:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_RESPONSES_HISTORY.value]
            indexes = Response.get_indexes()
            for index in indexes:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )

    async def insert_response(self, response: Response):
        result = await self.collection.insert_one(response.model_dump(by_alias=True, exclude_none=True))
        response.id = str(result.inserted_id)
        return response

    async def get_messages_by_session(self, session_id: str):
        cursor = self.collection.find(
            {"session_id": session_id}
        ).sort("created_at", 1)

        messages = []
        async for doc in cursor:
            messages.append(Response(**doc))

        return messages

    async def get_sessions_by_project(self, project_id: str):
        pipeline = [
            {"$match": {"response_project_id": project_id}},
            {"$sort": {"created_at": -1}},
            {"$group": {
                "_id": "$session_id",
                "session_id": {"$first": "$session_id"},
                "last_query": {"$first": "$user_query"},
                "last_answer": {"$first": "$output_text"},
                "created_at": {"$first": "$created_at"},
                "message_count": {"$sum": 1}
            }},
            {"$sort": {"created_at": -1}}
        ]

        cursor = await self.collection.aggregate(pipeline)
        sessions = []
        async for doc in cursor:
            sessions.append({
                "session_id": doc["session_id"],
                "last_query": doc["last_query"],
                "last_answer": doc["last_answer"],
                "created_at": doc["created_at"],
                "message_count": doc["message_count"]
            })

        return sessions

    async def delete_responses_by_project_id(self, project_id):
        result = await self.collection.delete_many({
            "response_project_id": project_id
        })
        return result.deleted_count

    async def delete_session(self, session_id: str):
        result = await self.collection.delete_many({
            "session_id": session_id
        })
        return result.deleted_count
