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


def generate_mock_post_referencing() -> BlogPostReferencing:
    """Referencing 패턴을 위한 목 포스트 데이터를 생성합니다."""

    post = BlogPostEmbedding(
        title="Sample Post with Embedding",
        content="This is a sample post using embedding pattern.",
        comments=[],  # 기본적으로 댓글이 없는 상태로 생성
    )


def generate_mock_comments_referencing(post_id: str) -> list[CommentReferencing]:
    """Referencing 패턴을 위한 목 댓글 데이터를 생성합니다."""
    return [
        CommentReferencing(post_id=post_id, author="Alice", content="Nice post!"),
        CommentReferencing(post_id=post_id, author="Bob", content="Very informative."),
    ]
