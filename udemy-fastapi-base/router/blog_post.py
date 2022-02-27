from typing import List, Optional
from fastapi import APIRouter, Body, Query
from pydantic import BaseModel

router = APIRouter(
    prefix='/blog',
    tags=['blog']
)

class BlogModel(BaseModel):
    title : str
    content: str
    nb_comments: int
    published: Optional[bool]

@router.post('/new')
def create_blog(blog: BlogModel, id: int, version: int = 1):
    return {
        'id': id,
        'data': blog,
        'version': version
        }
    
@router.post('/new/{id}/comment')
def create_comment(blog: BlogModel, id: int,
                    comment_id: int = Query(None,
                    title="ID of the Comment",
                    description='Some description for comment id',
                    alias='commentID'
                    ),
                    content: str = Body(...,
                                        min_length=10,
                                        max_length=50,
                                        regex='^[a-z\s]*$'
                                        ),
                    v: Optional[List[str]] = Query(None)
                ):
    return {
        'id': id,
        'data': blog,
        'comment_id': comment_id,
        'content': content,
        'versions':v
        }