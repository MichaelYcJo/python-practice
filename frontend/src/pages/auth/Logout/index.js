import Main from 'pages/home/Main';
import React from 'react'

const Logout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/';
    return (
        <Main />
    )
}

export default Logout