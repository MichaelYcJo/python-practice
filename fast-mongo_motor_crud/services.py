from bson import ObjectId
from database import mongo_instance
from schemas import BlogPostEmbedding, BlogPostReferencing, CommentReferencing
from mock_data import generate_mock_data_embedding, generate_mock_data_referencing


# Embedding 패턴 CRUD
async def create_post_embedding(post: BlogPostEmbedding):
    collection = mongo_instance.get_collection("blog_posts_embedding")

    post = generate_mock_data_embedding()

    result = await collection.insert_one(post.model_dump())
    return str(result.inserted_id)


async def get_post_embedding(post_id: str):
    collection = mongo_instance.get_collection("blog_posts_embedding")
    post = await collection.find_one({"_id": ObjectId(post_id)})
    return post


# Referencing 패턴 CRUD
async def create_post_referencing(post: BlogPostReferencing):
    post_collection = mongo_instance.get_collection("blog_posts_referencing")
    comment_collection = mongo_instance.get_collection("comments_referencing")

    post, comments = generate_mock_data_referencing()

    result = await post_collection.insert_one(post.dict())
    post_id = str(result.inserted_id)

    # Referencing 패턴에서는 댓글을 별도로 추가해야 합니다.
    for comment in comments:
        comment.post_id = post_id  # 포스트 ID를 댓글에 할당
        await comment_collection.insert_one(comment.dict())

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
