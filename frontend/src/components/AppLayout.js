import React from 'react'
import AppFooter from './AppFooter'
import AppHeader from './AppHeader'

export default function AppLayout(props) {
    const { children } = props
    return (
        <>
            <AppHeader />
            {children}
            <AppFooter />
        </>
    )
}
