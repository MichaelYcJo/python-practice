
import React, { useState } from "react";
import RegisterPresenter from './RegisterPresenter'

import api from 'api'

export const Register = () => {
    const [email, setEmail] = useState("");
    const [password, setPassword] = useState("")
    const [confirmPassword, setConfirmPassword] = useState("")
    const [firstName, setFirstName] = useState("");
    const [lastName, setLastName] = useState("");
    const [phoneNumber, setPhoneNumber] = useState("");
    const [toggleAuthInput, setToggleAuthInput] = useState(false)

    const onClick = () => {
        alert('아직 개발되지 않은 기능입니다')
        //setToggleAuthInput(true) //!toggleAuthInput
    }

    const isFormValid = () => {
        if (
            email === "" ||
            password === "" ||
            confirmPassword === "" ||
            firstName === "" ||
            lastName === "" ||
            phoneNumber === ""
        ) {
            alert("All fields are required.");
            return false;
        }
        return true;
    }

    const handleSubmit = async () => {
        if (!isFormValid()) {
            return;
        }
        //setLoading(true);
        try {
            const { status } = await api.createAccount({
                email,
                password,
                confirm_password: confirmPassword,
                first_name: firstName,
                last_name: lastName,
                phone: phoneNumber,

            });
            if (status === 201) {
                alert("Account created. Sign in, please.");
                //navigate("SignIn", { email, password });
            }
        } catch (e) {
            alert("The email is taken");
        } finally {
            //setLoading(false);
        }
    };

    return (
        <RegisterPresenter
            email={email}
            setEmail={setEmail}
            password={password}
            setPassword={setPassword}
            confirmPassword={confirmPassword}
            setConfirmPassword={setConfirmPassword}
            firstName={firstName}
            setFirstName={setFirstName}
            lastName={lastName}
            setLastName={setLastName}
            phoneNumber={phoneNumber}
            setPhoneNumber={setPhoneNumber}
            toggleAuthInput={toggleAuthInput}
            onClick={onClick}
            handleSubmit={handleSubmit}
        />
    )
}

export default Register