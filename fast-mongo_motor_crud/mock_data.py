from schemas import BlogPostEmbedding, BlogPostReferencing, Comment, CommentReferencing


def generate_mock_data_embedding() -> BlogPostEmbedding:
    """Embedding 패턴을 위한 목 데이터를 생성합니다."""
    return BlogPostEmbedding(
        title="Sample Post with Embedding",
        content="This is a sample post using embedding pattern.",
        comments=[
            Comment(author="Alice", content="Nice post!"),
            Comment(author="Bob", content="Very informative."),
        ],
    )


def generate_mock_data_referencing() -> (BlogPostReferencing, list[CommentReferencing]):
    """Referencing 패턴을 위한 목 데이터를 생성합니다."""
    post = BlogPostReferencing(
        title="Sample Post with Referencing",
        content="This is a sample post using referencing pattern.",
    )

    comments = [
        CommentReferencing(post_id=None, author="Alice", content="Nice post!"),
        CommentReferencing(post_id=None, author="Bob", content="Very informative."),
    ]

    return post, comments
