from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID


class HSCodeBase(BaseModel):
    code: str
    description: str
    parent_code: Optional[str] = None
    level: str
    country: str = "US"


class HSCodeResponse(HSCodeBase):
    id: UUID
    
    class Config:
        from_attributes = True


class HSCodeSearchResult(BaseModel):
    results: List[HSCodeResponse]
    total: int
    query: str
