from pydantic import BaseModel
from typing import Generic, TypeVar, Optional

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    items: list[T]
    total: int
    limit: int
    offset: int


class MessageResponse(BaseModel):
    message: str


class TaskQueued(BaseModel):
    task_id: str
    message: str
