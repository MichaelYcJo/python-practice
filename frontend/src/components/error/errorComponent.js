import React from 'react'

export default function errorComponent({message}) {
    return (
        <div className='error_message'>
            {message}
        </div>
    )
}
