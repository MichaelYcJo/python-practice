from fastapi import FastAPI, HTTPException
from exceptions.error_list import PostExceptions
from schemas import BlogPostEmbedding, BlogPostReferencing, CommentReferencing
import services

app = FastAPI()
app.add_exception_handler(HTTPException, services.global_exception_handler)


@app.post("/posts/embedding")
async def create_post_embedding(post: BlogPostEmbedding):
    post_id = await services.create_post_embedding(post)
    return {"id": post_id}


@app.get("/posts/embedding/{post_id}")
async def get_post_embedding(post_id: str):
    post = await services.get_post_embedding(post_id)
    if post is None:
        raise PostExceptions.NotFoundPost()
    return post


@app.post("/posts/referencing")
async def create_post_referencing(post: BlogPostReferencing):
    post_id = await services.create_post_referencing(post)
    return {"id": post_id}


@app.post("/comments/referencing")
async def add_comment_referencing(comment: CommentReferencing):
    comment_id = await services.add_comment_referencing(comment)
    if comment_id is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"id": comment_id}


@app.get("/posts/referencing/{post_id}")
async def get_post_with_comments(post_id: str):
    post_with_comments = await services.get_post_with_comments(post_id)
    if post_with_comments is None:
        raise HTTPException(status_code=404, detail="Post not found")
    return post_with_comments
