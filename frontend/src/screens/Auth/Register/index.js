
import React, { useState } from "react";
import RegisterPresenter from './RegisterPresenter'

export const Login = () => {
    const [userName, setUserName] = useState("");
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("")
    const [toggleAuthInput, setToggleAuthInput] = useState(false)

    const onClick = () => {
        setToggleAuthInput(true) //!toggleAuthInput
    }

    const isFormValid = () => {
        if (
            userName === "" ||
            email === "" ||
            password === ""
        ) {
            alert("All fields are required.");
            return false;
        }
    }

    const handleSubmit = () => {
        if (!isFormValid()) {
            return;
        }
    }

    return (
        <RegisterPresenter
            userName={userName}
            setUserName={setUserName}
            email={email}
            setEmail={setEmail}
            password={password}
            setPassword={setPassword}
            toggleAuthInput={toggleAuthInput}
            onClick={onClick}
            handleSubmit={handleSubmit}
        />
    )
}

export default Login