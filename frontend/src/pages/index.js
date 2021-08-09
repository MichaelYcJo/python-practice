import React from 'react'
import AppLayout from 'components/AppLayout'
import { Route } from 'react-router-dom'
import AccountsRoutes from "./accounts"
import About from './About'
import Home from './Home'
import LoginRequiredRoute from "utils/LoginRequiredRoute";

export default function Root() {
    return (
        <AppLayout >
            <LoginRequiredRoute exact path="/" component={Home} />
            <Route exact path="/about" component={About} />
            <Route path="/accounts" component={AccountsRoutes} />
        </ AppLayout >

    )
}
