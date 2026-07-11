from typing import Optional
from pydantic import BaseModel

class ProcessRequest(BaseModel):
    file_id:str=None
    chunk_size:Optional[int]=500
    overlap_size: Optional[int]=50
    do_reset: Optional[int]=0
    
