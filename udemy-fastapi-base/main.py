from typing import Optional
from fastapi import FastAPI
from enum import Enum

app = FastAPI()

@app.get('/blog/all')
def get_all_blogs(page, page_size : Optional[int] = None):
    return{'message': f'All blogs {page}, of {page_size}'}

@app.get('/blog/{id}/comments/{comment_id}')
def get_comment(id: int, comment_id: int, valid: bool = True, username: Optional[str] = None):
    return {'message': f'Blog {id} comment {comment_id} is valid: {valid}, username {username}'}

class BlogType(str, Enum):
    short = 'short'
    story = 'story'
    howto = 'howto'
    
@app.get('/blog/type/{type}')
def get_blog_type(type: BlogType):
    return {'message': f'{type} blogs'}

@app.get('/blog/{id}')
def get_blog(id: int):
    return {"message": f"Blog post number id: {id}"}


