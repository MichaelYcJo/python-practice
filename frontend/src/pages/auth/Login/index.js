import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useRecoilState } from "recoil";
import { userState } from "recoil/userRecoil";

import {LoginAxiosInstance} from "api";
import LoginPresenter from "pages/auth/Login/LoginPresenter";
import {KAKAO_AUTH_URL} from 'components/kakao/socialLogin'


const Login = ({location}) => {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [userInfo, setUserInfo] = useRecoilState(userState)
  const [errorType, setErrorType] = useState("")
  const [error, setError] = useState("");

  const redirect = location.search ? location.search.split('=')[1] : '/'

  useEffect(() => {
      if (userInfo.access_token) {
          window.location = redirect
      }
  }, [userInfo, redirect])


  
  const isFormValid = () => {
    if (email === "" || password === "") {
      setErrorType('required')
      setError('All Fields Are Required')
      return false;
    }

    return true;
};
const handleSubmit = async (e) => {
    e.preventDefault();

    if (!isFormValid()) {
        return;
    }
    const formData = { email, password }
    try {
        const { status, data } = await LoginAxiosInstance.post(
            '/accounts/login', formData);
        if (status === 200) {
            const { access, refresh } = data;
            setUserInfo({ 'access_token': access, 'refresh_token': refresh, 'isLoggedIn': true });
            localStorage.setItem('access_token', access);
            localStorage.setItem('refresh_token', refresh);
        }
    } catch (e) {
        const status_code = e.response.status;
        if (status_code === 401) {
            setErrorType('invalid')
            setError('유효하지않은 이메일 또는 패스워드입니다')
        } else {
            alert('API Connect Failed')
        }
    } finally {
        //setLoading(false);
    }

};



const kakaoLogin = () => {
    window.location.href = KAKAO_AUTH_URL
}

  return (
      <LoginPresenter 
      email={email}
      setEmail={setEmail}
      password={password}
      setPassword={setPassword}
      error={error}
      setError={setError}
      errorType={errorType}
      setErrorType={setErrorType}
      handleSubmit={handleSubmit}
      kakaoLogin={kakaoLogin}
      />
   
  );
};

Login.propTypes = {
  location: PropTypes.object
};

export default Login;
