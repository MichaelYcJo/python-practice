from typing import List, Optional
from fastapi import APIRouter, Body, Path, Query
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
    
@router.post('/new/{id}/comment/{comment_id}')
def create_comment(blog: BlogModel, id: int,
                    comment_title: int = Query(None,
                    title="Title of the Comment",
                    description='Some description for comment Title',
                    alias='commentTitle'
                    ),
                    content: str = Body(...,
                                        min_length=10,
                                        max_length=50,
                                        regex='^[a-z\s]*$'
                                        ),
                    v: Optional[List[str]] = Query(None),
                    comment_id: int = Path(None, gt=5, le=10)
                ):
    return {
        'id': id,
        'data': blog,
        'comment_title': comment_title,
        'content': content,
        'versions':v,
        'comment_id': comment_id,
        }