import React, { useEffect, useState } from 'react'
import Axios from 'axios';

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
            <h2>PostList</h2>
            {postList.map(post => {
                const { caption, location, photo } = post;
                return (
                    <div key={post.id}>
                        {caption}, {location}
                        <img alt='귀여운고퍼' src={photo} style={{ width: '100px' }} />
                    </div>
                )
            }
            )}
        </div>
    );
}
