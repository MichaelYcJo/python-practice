import { Avatar, Card } from 'antd'
import React from 'react'
import { HeartFilled, UserOutlined } from '@ant-design/icons';

export default function Post({ post }) {
    return (
        <div>
            <Card cover={<img src={post.photo} alt={post.caption} />}
                actions={[<HeartFilled />]}
            >
                <Card.Meta
                    avatar={
                        <Avatar
                            size="large"
                            icon={<UserOutlined />}
                        />
                    } title={post.location} description={post.caption} />
                {post.caption}, {post.location}
                <img alt='귀여운고퍼' src={post.photo} style={{ width: '100px' }} />
            </Card>
        </div>
    )
}

