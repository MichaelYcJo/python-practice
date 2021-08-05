import React, { useEffect, useState } from 'react'
import Axios from 'axios';
import Post from './Post';

const apiUrl = "http://localhost:8000/api/posts/"

export default function PostList() {
    const [postList, setPostList] = useState([]);
    useEffect(() => {
        Axios.get(apiUrl)
            .then(response => {
                const { data } = response
                setPostList(data)
            })
            .catch(error => {
                console.log('실패시', error)
            })
    }, [])

    return (
        <div>
            {postList.map(post => <Post key={post.id} post={post} />
            )}
        </div>
    );
}
