import React from "react";
import { Route, Redirect } from "react-router-dom";
import { useAppContext } from "store";

export default function LoginRequiredRoute({
    component: Component,
    ...kwargs
}) {
    const {
        store: { isAuthenticated }
    } = useAppContext();

    console.log("isAuthenticated", isAuthenticated);

    if (isAuthenticated) {
    } else {
    }

    return (
        <Route
            {...kwargs}
            render={props => {
                if (isAuthenticated) {
                    return <Component {...props} />;
                } else {
                    return (
                        <Redirect
                            to={{
                                pathname: "/accounts/login",
                                state: { from: props.location }
                            }}
                        />
                    );
                }
            }}
        />
    );
}