from pydantic import BaseModel, Field
from typing import List, Optional


class Comment(BaseModel):
    post_id: str
    author: str
    content: str


class BlogPostEmbedding(BaseModel):
    title: str
    content: str
    comments: List[Comment] = []


class BlogPostReferencing(BaseModel):
    title: str
    content: str
    comment_ids: Optional[List[str]] = Field(default=[])


class CommentReferencing(BaseModel):
    post_id: str
    author: str
    content: str
