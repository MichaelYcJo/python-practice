from bson import ObjectId
from database import mongo_instance
from schemas import BlogPostEmbedding, BlogPostReferencing, CommentReferencing
from mock_data import generate_mock_post_referencing, generate_mock_comments_referencing

# solution:  https://stackoverflow.com/questions/76727389/why-doesnt-fastapi-return-my-mongodb-objects
from fastapi.encoders import ENCODERS_BY_TYPE

ENCODERS_BY_TYPE[ObjectId] = str


# Embedding 패턴 CRUD
async def create_post_embedding(post: BlogPostEmbedding):
    collection = mongo_instance.get_collection("blog_posts_embedding")

    # generate_mock_data_embedding 함수는 따로 변경할 필요 없음
    post = BlogPostEmbedding(
        title=post.title,
        content=post.content,
        comments=[],  # 기본적으로 댓글이 없는 상태로 생성
    )

    result = await collection.insert_one(post.model_dump())
    return str(result.inserted_id)


async def get_post_embedding(post_id: str):
    collection = mongo_instance.get_collection("blog_posts_embedding")
    post = await collection.find_one({"_id": ObjectId(post_id)})
    return post


# Referencing 패턴 CRUD
# Referencing 패턴 CRUD
async def create_post_referencing(post: BlogPostReferencing):
    post_collection = mongo_instance.get_collection("blog_posts_referencing")

    post = BlogPostReferencing(title=post.title, content=post.content, comment_ids=[])

    result = await post_collection.insert_one(post.model_dump())
    post_id = str(result.inserted_id)

    # 댓글을 생성하기 위해 해당 포스트의 post_id를 전달
    comments = generate_mock_comments_referencing(post_id)

    comment_collection = mongo_instance.get_collection("comments_referencing")
    comment_ids = []
    for comment in comments:
        comment_result = await comment_collection.insert_one(comment.model_dump())
        comment_ids.append(str(comment_result.inserted_id))

    # 포스트 문서에 댓글 ID 리스트 추가
    await post_collection.update_one(
        {"_id": ObjectId(post_id)}, {"$set": {"comment_ids": comment_ids}}
    )

    return post_id


async def add_comment_referencing(comment: CommentReferencing):
    post_collection = mongo_instance.get_collection("blog_posts_referencing")
    comment_collection = mongo_instance.get_collection("comments_referencing")

    post = await post_collection.find_one({"_id": ObjectId(comment.post_id)})
    if not post:
        return None

    result = await comment_collection.insert_one(comment.dict())
    return str(result.inserted_id)


async def get_post_with_comments(post_id: str):
    post_collection = mongo_instance.get_collection("blog_posts_referencing")
    comment_collection = mongo_instance.get_collection("comments_referencing")

    post = await post_collection.find_one({"_id": ObjectId(post_id)})
    if post is None:
        return None

    comments = await comment_collection.find({"post_id": post_id}).to_list(length=100)
    return {**post, "comments": comments}
