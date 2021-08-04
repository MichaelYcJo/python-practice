import React from 'react'
import { Route } from 'react-router-dom'
import Login from './Login'
import Profile from './Profile'

export default function Routes({ match }) {
    return (
        <>
            <Route exact path={match.url + "/profile"} component={Profile} />
            <Route exact path={match.url + "/login"} component={Login} />
        </>
    )
}
