from typing import List, Optional, Dict
from datetime import datetime
from pydantic import BaseModel, field_validator


class StoryOptionsSchema(BaseModel):
    text: str
    node_id: Optional[int] = None


class StoryNodeBase(BaseModel):
    content: str
    is_ending: bool = False
    is_winning_ending: bool = False


class CompleteStoryNodeResponse(StoryNodeBase):
    id: int
    options: List[StoryOptionsSchema] = []

    class Config:
        from_attributes = True


class StoryBase(BaseModel):
    title: str
    session_id: Optional[str] = None

    class Config:
        from_attributes = True


class CreateStoryRequest(BaseModel):
    theme: str

    @field_validator("theme")
    @classmethod
    def validate_theme(cls, value: str) -> str:
        if not value or not value.strip():
            raise ValueError("theme must not be empty")
        return value.strip()


class CompleteStoryResponse(StoryBase):
    id: int
    created_at: datetime
    root_node: CompleteStoryNodeResponse
    all_nodes: Dict[int, CompleteStoryNodeResponse]

    class Config:
        from_attributes = True