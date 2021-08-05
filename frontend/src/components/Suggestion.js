import React from 'react'
import { UserOutlined } from '@ant-design/icons';
import { Avatar, Button } from "antd";
import "./Suggestion.scss";

export default function Suggestion() {
    return (
        <div className="suggestion">
            <div className="avatar">
                <UserOutlined />
                <div className="username">username </div>
                <div className="action">
                    <Button size="small">Follow</Button>
                </div>
            </div>
        </div>
    )
}
