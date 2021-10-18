import React, {useState} from "react";
import PropTypes from "prop-types";

import AxiosInstance from 'api'
import RegisterPresenter from "pages/auth/Register/RegisterPresenter";

const Regitser = () => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("")
  const [confirmPassword, setConfirmPassword] = useState("")
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [errorType, setErrorType] = useState("")
  const [error, setError] = useState("");

  const isFormValid = () => {
    if (
        email === "" ||
        password === "" ||
        confirmPassword === "" ||
        firstName === "" ||
        lastName === "" ||
        phoneNumber === ""
    ) {
        setErrorType('blank')
        setError("All fields are required")
        return false;
    }
    return true;
}

const handleSubmit = async (e) => {
    e.preventDefault();
    if (!isFormValid()) {
        return;
    }
    //setLoading(true);
    try {
        const { status, data } = await AxiosInstance.post(
            "/accounts/register", {
            email,
            password,
            confirm_password : confirmPassword,
            first_name: firstName,
            last_name: lastName,
            phone: phoneNumber,

        });
        if (status === 201) {
            alert("Account created. Sign in, please.");
            //location Login
            window.location.href = "/accounts/login"

            //navigate("SignIn", { email, password });
        } else if (status === 202) {
            if (data.email) {
                setErrorType("email")
                setError(data.email[0])
            }
        }
    } catch (e) {
        const status_code = e.response.status;
        if (status_code === 400) {
            if (e.response.data.email) {
                setErrorType('email')
                setError(e.response.data.email)
            }
            if (e.response.data.password) {
                setErrorType('password')
                setError(e.response.data.password)
            }
        } else {
            alert('API Connect Failed')
        }
        //alert("The email is taken");
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
      handleSubmit={handleSubmit}
      error={error}
      errorType={errorType} 
      />
   
  );
};

Regitser.propTypes = {
  location: PropTypes.object
};

export default Regitser;




