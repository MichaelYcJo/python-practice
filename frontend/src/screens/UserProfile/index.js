import React from "react";
import { useRecoilValue } from 'recoil';
import { userState } from 'recoil/userRecoil'

import axiosInstance from 'api'
import UserProfilePresenter from "./UserProfilePresenter";


export const UserProfile = () => {
    const { access_token } = useRecoilValue(userState)
    try {
        const { status, data } = axiosInstance.get('/accounts/profile/')
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



