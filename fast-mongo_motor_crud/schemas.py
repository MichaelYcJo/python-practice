from pydantic import BaseModel
from typing import List, Optional


class Comment(BaseModel):
    author: str
    content: str


class BlogPostEmbedding(BaseModel):
    title: str
    content: str
    comments: List[Comment] = []


class BlogPostReferencing(BaseModel):
    title: str
    content: str


class CommentReferencing(BaseModel):
    post_id: str
    author: str
    content: str
