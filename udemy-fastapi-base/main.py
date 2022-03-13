from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, PlainTextResponse
from exceptions import StoryException
from router import article, blog_get, blog_post, user, product
from auth import authentication
from db import models
from db.database import engine

app = FastAPI()
app.include_router(authentication.router)
app.include_router(article.router)
app.include_router(user.router)
app.include_router(blog_get.router)
app.include_router(blog_post.router)
app.include_router(product.router)

@app.get('/hello')
def index():
  return {'message': 'Hello world!'}

@app.exception_handler(StoryException)
def story_exception_handler(request: Request, exc: StoryException):
  return JSONResponse(
    status_code=410,
    content={'detail': exc.name}
  )


@app.exception_handler(HTTPException)
def custom_handler(request: Request, exc: StoryException):
  return PlainTextResponse(str(exc), status_code=400)
  

models.Base.metadata.create_all(engine)\

origins = [
           'http://localhost:3000',
           ]

app.add_middleware(
  CORSMiddleware,
  allow_origins = origins,
  allow_credentials = True,
  allow_methods = ["*"],
  allow_headers = ['*']
)