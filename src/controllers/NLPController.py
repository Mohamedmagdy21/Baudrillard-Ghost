from ipaddress import collapse_addresses

from stores.llm.templates.locales.en.rag import footer_prompt
from .BaseController import BaseController
from src.models.db_schema.data_chunk import DataChunk
from src.models.db_schema.project import  project
from src.stores.vectordb.providers.QdrantDB import QdrantDB
from src.models.ChunkModel import ChunkModel
from src.stores.llm.LLMEnums import DocumentTypeEnum
import asyncio
from src.stores.llm.templates.template_parser import TemplateParser
import enum



class NLPController(BaseController):

    def __init__(self,vectordb_client,embedding_model,generation_model,template_parser:TemplateParser):

        super().__init__()

        self.vectordb_client=vectordb_client
        self.embedding_model=embedding_model
        self.generation_model=generation_model
        self.template_parser=template_parser

    def create_collection_name(self,project_id:str):
        return f"collection_{project_id}".strip()    


    def reset_vector_db_collection(self,project:project):
        collection_name=self.create_collection_name(project_id=project.project_id)
        return self.vectordb_client.delete_collection(collection_name=collection_name)

    def get_vector_db_collection_info(self,project:project)  :
        collection_name=self.create_collection_name(project_id=project.project_id)  
        return self.vectordb_client.get_collection_info(collection_name=collection_name)


    async def index_into_vector_db(self,project:project,chunks:list[DataChunk],chunk_ids:list[int],do_reset:bool=False):

        # get collection
        collection_name=self.create_collection_name(project_id=project.project_id)

        
        # manage items

        text_list=[text.chunk_text for text in chunks]
        meta_data=[text.chunk_metadata for text in chunks]


        # index them and insert into db
        self.vectordb_client.create_collection(collection_name=collection_name, collection_size=self.embedding_model.embedding_dimensions, do_reset=do_reset)
        ##vectors=[self.embedding_model.embed_text( text=text , document_type=DocumentTypeEnum.DOCUMENT.value) for text in text_list ]
       # vectors = []
        #for text in text_list:
         #   vector = self.embedding_model.embed_text(text=text, document_type=DocumentTypeEnum.DOCUMENT.value)
          #  vectors.append(vector)
           # await asyncio.sleep(0.7)
        vectors = await asyncio.to_thread(
            lambda: self.embedding_model.embed_text_batch(texts=text_list, document_type=DocumentTypeEnum.DOCUMENT.value)
        )   

        self.vectordb_client.insert_many(collection_name=collection_name, texts=text_list, vectors=vectors, metadatas=meta_data,record_ids=chunk_ids)
        



        return True

    def search_vector_db_collection(self,project:project,text:str,limit:int) :

       # step 1: get collection name
       collection_name=self.create_collection_name(project_id=project.project_id)
        
       # step 2: get text embedding vector
       vector=self.embedding_model.embed_text(
        text=text,
        document_type=DocumentTypeEnum.Query.value

       )
       if not vector or len(vector)==0:
        return False

        # step 3: do semantic search  

       retrieved_list=self.vectordb_client.search_by_vector(collection_name=collection_name, vector=vector, limit=5)

       if not retrieved_list:
        return False

       return retrieved_list


    def answer_rag_question(self,project:project,query:str,limit:int): 

        #step1 : retrieve related docs

        retrieved_docs=self.search_vector_db_collection(
            project=project,
            text=query,
            limit=limit,
        )

        if not retrieved_docs:
            return None

        # step 2 : construct LLM Prompt
        system_prompt=self.template_parser.get(group="rag",key="system_prompt",)   

        
        document_prompts="\n".join([
            self.template_parser.get("rag","document_type",vars={"doc_num":idx,"content":doc.text})
            for idx,doc in enumerate(retrieved_docs)
        ])

        footer_prompt=self.template_parser.get("rag","footer_prompt")


        user_prompt=self.template_parser.get("rag",query)

        full_prompt="\n\n".join([document_prompts,user_prompt,footer_prompt])

        response=self.generation_model.generate_text(system_prompt=system_prompt, user_prompt=full_prompt)
