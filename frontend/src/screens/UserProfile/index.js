import React from "react";
import { useRecoilValue } from 'recoil';
import { userState } from 'recoil/userRecoil'

import api from 'api'
import UserProfilePresenter from "./UserProfilePresenter";


export const UserProfile = () => {
    const { token } = useRecoilValue(userState)
    try {
        const { status, data } = api.userProfile(token);
        if (status === 200) {
            console.log(data);
        }
    } catch (e) {
        console.log(e.response);
        console.log(e.response.data);
        console.log(e.response.message);
    }

    return (

        <UserProfilePresenter />


    )

}

export default UserProfile



