from bson import ObjectId
from database import mongo_instance
from schemas import BlogPostEmbedding, BlogPostReferencing, CommentReferencing


# Embedding 패턴 CRUD
async def create_post_embedding(post: BlogPostEmbedding):
    collection = mongo_instance.get_collection("blog_posts_embedding")
    result = await collection.insert_one(post.model_dump(mode="json"))
    return str(result.inserted_id)


async def get_post_embedding(post_id: str):
    collection = mongo_instance.get_collection("blog_posts_embedding")
    post = await collection.find_one({"_id": ObjectId(post_id)})
    return post


# Referencing 패턴 CRUD
async def create_post_referencing(post: BlogPostReferencing):
    collection = mongo_instance.get_collection("blog_posts_referencing")
    result = await collection.insert_one(post.model_dump(mode="json"))
    return str(result.inserted_id)


async def add_comment_referencing(comment: CommentReferencing):
    post_collection = mongo_instance.get_collection("blog_posts_referencing")
    comment_collection = mongo_instance.get_collection("comments_referencing")

    post = await post_collection.find_one({"_id": ObjectId(comment.post_id)})
    if not post:
        return None

    result = await comment_collection.insert_one(comment.model_dump(mode="json"))
    return str(result.inserted_id)


async def get_post_with_comments(post_id: str):
    post_collection = mongo_instance.get_collection("blog_posts_referencing")
    comment_collection = mongo_instance.get_collection("comments_referencing")

    post = await post_collection.find_one({"_id": ObjectId(post_id)})
    if post is None:
        return None

    comments = await comment_collection.find({"post_id": post_id}).to_list(length=100)
    return {**post, "comments": comments}
