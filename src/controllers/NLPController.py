from ipaddress import collapse_addresses
import time
import uuid

from src.stores.llm.templates.locales.en.rag import footer_prompt
from .BaseController import BaseController
from src.models.db_schema.data_chunk import DataChunk
from src.models.db_schema.project import  project
from src.models.db_schema.AgenticResponseModel import AgenticResponseModel
from src.models.db_schema.response import Response
from src.stores.vectordb.providers.QdrantDB import QdrantDB
from src.models.ChunkModel import ChunkModel
from src.stores.llm.LLMEnums import DocumentTypeEnum
import asyncio
from src.stores.llm.templates.template_parser import TemplateParser
from loguru import logger





class NLPController(BaseController):

    def __init__(self,vectordb_client,embedding_model,generation_model,query_rewriter_agent,template_parser:TemplateParser,reranker_client=None,rerank_top_n:int=5,reranker_candidates:int=20,response_model=None):

        super().__init__()

        self.vectordb_client=vectordb_client
        self.embedding_model=embedding_model
        self.generation_model=generation_model
        self.template_parser=template_parser
        self.query_rewriter_agent = query_rewriter_agent
        self.reranker_client = reranker_client
        self.rerank_top_n = rerank_top_n
        self.reranker_candidates = reranker_candidates
        self.response_model = response_model

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

       retrieved_list= self.vectordb_client.search_by_vector(collection_name=collection_name, vector=vector, limit=5)

       if not retrieved_list:
        return False

       return retrieved_list


    def answer_rag_question(self,project:project,query:str,limit:int): 

        #step1 : retrieve related docs (over-fetch if reranker is configured)

        search_limit = self.reranker_candidates if self.reranker_client else limit

        results= self.query_rewriter_agent.run(
            query=query,
            project=project,
            collection_name=self.create_collection_name(project.project_id),
            limit=search_limit
        )



        if not results.retrieved_docs:
            return None

        # step 1.5 : rerank retrieved docs with cross-encoder if configured
        if self.reranker_client:
            top_n = self.rerank_top_n or limit
            reranked = self.reranker_client.rerank(
                query=results.rewritten,
                documents=results.retrieved_docs,
                top_n=top_n,
            )
            if reranked:
                doc_texts = [doc.text for doc in reranked]
            else:
                doc_texts = results.retrieved_docs[:limit]
        else:
            doc_texts = results.retrieved_docs[:limit]

        # step 2 : construct LLM Prompt
        system_prompt=self.template_parser.get(group="rag",key="system_prompt",)   

        
        document_prompts="\n".join([
            self.template_parser.get("rag","document_prompt",vars={"doc_num":idx,"chunk_text":doc})
            for idx,doc in enumerate(doc_texts)
        ])

        footer_prompt=self.template_parser.get("rag","footer_prompt")


        user_prompt=self.template_parser.get("rag", "user_query", vars={"user_query": results.rewritten})

        ####### REMINDER: CHAT HISTORY DOESNOT EXIST IN THE GENERTATE TEXT
       # chat_history=self.generation_model.construct_prompt(
        #    prompt=system_prompt,
         #   role=self.generation_model.enums.SYSTEM.value

        #)

        full_prompt="\n\n".join([document_prompts,user_prompt,footer_prompt])

        response=self.generation_model.generate_text(system_prompt=system_prompt, user_prompt=full_prompt,max_output_tokens=self.generation_model.default_output_max_tokens)

       # response = self.generation_model.generate_text(
        #prompt=f"{system_prompt}\n\n{full_prompt}",
        #max_output_tokens=1024
        #)

        return response, full_prompt


    async def chat_rag_question(self, project: project, query: str, limit: int, session_id: str = None):

        # generate session_id if not provided
        if not session_id:
            session_id = str(uuid.uuid4())

        # load chat history from DB
        chat_history_msgs = []
        if self.response_model:
            db_messages = await self.response_model.get_messages_by_session(session_id=session_id)
            for msg in db_messages:
                chat_history_msgs.append({"role": "user", "content": msg.user_query})
                chat_history_msgs.append({"role": "assistant", "content": msg.output_text})

            logger.info(f"[CHAT] session={session_id} history_msgs={len(chat_history_msgs)}")

        # step 1: check if collection exists
        collection_name = self.create_collection_name(project.project_id)
        if not self.vectordb_client.does_collection_exist(collection_name=collection_name):
            logger.warning(f"[CHAT] collection {collection_name} does not exist")
            return None, None, session_id

        #############################################################################################    

        # step 2: retrieve (over-fetch if reranker)
       # search_limit = self.reranker_candidates if self.reranker_client else limit

      #  results = self.query_rewriter_agent.run(
       #     query=query,
        #    project=project,
        #    collection_name=collection_name,
        #    limit=search_limit
        #)

        #if not results.retrieved_docs:
        #    return None, None, session_id

        # step 1.5: rerank
        #if self.reranker_client:
         #   top_n = self.rerank_top_n or limit
         #   reranked = self.reranker_client.rerank(
         #       query=results.rewritten,
         #       documents=results.retrieved_docs,
         #       top_n=top_n,
         #   )
         #   doc_texts = [doc.text for doc in reranked] if reranked else results.retrieved_docs[:limit]
        #else:
        #    doc_texts = results.retrieved_docs[:limit]

        ###################################################################################################  
        # 
        vector = self.embedding_model.embed_text(query, document_type=DocumentTypeEnum.Query.value)
        doc_texts = self.vectordb_client.search_by_vector(collection_name, vector, limit=limit)
  

        # step 2: construct prompt
        system_prompt = self.template_parser.get(group="rag", key="system_prompt")

        document_prompts = "\n".join([
            self.template_parser.get("rag", "document_prompt", vars={"doc_num": idx, "chunk_text": doc})
            for idx, doc in enumerate(doc_texts)
        ])

        footer_prompt = self.template_parser.get("rag", "footer_prompt")
        #user_prompt = self.template_parser.get("rag", "user_query", vars={"user_query": results.rewritten})
        user_prompt = self.template_parser.get("rag", "user_query", vars={"user_query": query})

        full_prompt = "\n\n".join([document_prompts, user_prompt, footer_prompt])

        # step 3: generate with chat history
        response = self.generation_model.generate_text(
            system_prompt=system_prompt,
            user_prompt=full_prompt,
            max_output_tokens=self.generation_model.default_output_max_tokens,
            chat_history=chat_history_msgs
        )

        if not response:
            return None, None, session_id

        # step 4: save to DB
        if self.response_model:
            resp_record = Response(
                session_id=session_id,
                response_project_id=project.id,
                user_query=query,
                output_text=response,
                created_at=time.time()
            )
            await self.response_model.insert_response(resp_record)
            logger.info(f"[CHAT] saved response to session={session_id}")

        return response, full_prompt, session_id
