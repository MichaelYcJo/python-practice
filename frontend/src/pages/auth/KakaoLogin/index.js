import axios from 'axios';
import React, { useEffect } from 'react'
import { useRecoilState } from "recoil";
import { kakaoState } from 'recoil/userRecoil';

const KakaoLogin = (props)  =>{

    const code = new URL(window.location.href).searchParams.get("code");
    const [kakaoCode, setkakaoCode] = useRecoilState(kakaoState)
    console.log(code, '흠');

    useEffect(() => {
        if(code){
            console.log(code, '코드');
            setkakaoCode(code)
            console.log(kakaoCode, '카카오코드ee');

            const fetchData = async () => {
                const result = await axios(
                    `http://127.0.0.1:8000/api/v1/accounts/login/kakao/callback?code=${code}`,
                );
              };
              // 실행함으로써 데이타를 fetching합니다.
              fetchData();

        }

      


    }, [code, kakaoCode, setkakaoCode])

    console.log(kakaoCode, '카카오코드effect이후');
    
    return (
        <div>
            카카오로그인핸들링페이지
        </div>
    )
}

export default KakaoLogin