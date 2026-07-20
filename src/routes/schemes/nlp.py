from typing import Optional
from pydantic import BaseModel

class PushRequest(BaseModel):
    do_reset:Optional[int]=0


class SearchRequest(BaseModel):
    text:str   
    limit: Optional[int]=5


class ChatRequest(BaseModel):
    text: str
    limit: Optional[int] = 5
    session_id: Optional[str] = None
