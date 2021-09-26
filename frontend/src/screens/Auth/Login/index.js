
import React, { useState, useEffect } from "react";
import LoginPresenter from "./LoginPresenter";
import api from 'api'
import { useRecoilState } from "recoil";
import { userState } from "recoil/userRecoil";


export const Login = ({ location, history }) => {

    const [userInfo, setUserInfo] = useRecoilState(userState)
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("");
    const [errorType, setErrorType] = useState("")
    const [error, setError] = useState("");

    const redirect = location.search ? location.search.split('=')[1] : '/'


    useEffect(() => {
        if (userInfo.token) {
            history.push(redirect)
        }
    }, [history, userInfo, redirect])

    const isFormValid = () => {
        if (email === "" || password === "") {
            alert("All fields are required.");
            return false;
        }

        return true;
    };
    const handleSubmit = async () => {
        if (!isFormValid()) {
            return;
        }
        const formData = { email, password }
        try {
            const { status, data } = await api.login(formData);
            if (status === 200) {
                const { access } = data;
                setUserInfo({ 'token': access, 'isLoggedIn': true });
                localStorage.setItem('token', access);
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
        />

    )
}

export default Login