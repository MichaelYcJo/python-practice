import React from 'react'

export default function Post({ post }) {
    return (
        <div>
            {post.caption}, {post.location}
            <img alt='귀여운고퍼' src={post.photo} style={{ width: '100px' }} />
        </div>
    )
}
