import axios from 'axios';
import React, { useEffect } from 'react'
import { useSetRecoilState } from "recoil";
import { kakaoState } from 'recoil/userRecoil';
import LoginPresenter from '../Login/LoginPresenter';


const KakaoLogin = (props)  =>{

    const code = new URL(window.location.href).searchParams.get("code");
    const setkakaoCode = useSetRecoilState(kakaoState)

    const fetchData = async ({history}) => {
        await axios({
            method: "GET",
            url:`http://127.0.0.1:8000/api/v1/accounts/login/kakao/callback?code=${code}`,

        })
        .then((res) => {
            const ACCESS_TOKEN = res.data.access_token;
            const REFRESH_TOKEN = res.data.refresh_token;
 
            localStorage.setItem('access_token', ACCESS_TOKEN);
            localStorage.setItem('refresh_token', REFRESH_TOKEN);
            window.location.href = '/';

        }).catch((err) => {
            window.alert("로그인에 실패하였습니다.");
            history.replace("/accounts/login"); // 로그인 실패하면 로그인화면으로 돌려보냄
            })
        }

    useEffect(() => {
        if(code){
            setkakaoCode(code)
            fetchData(props);
        }
    }, [code])
    
    return (
        <LoginPresenter />
    )
}

export default KakaoLogin