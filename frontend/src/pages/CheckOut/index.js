import React, {useState} from "react";
import Login from "pages/auth/Login";
import PropTypes from "prop-types";
import { connect } from "react-redux";
import { useRecoilValue } from "recoil";
import { userState } from "recoil/userRecoil";

import CheckOutPresenter from "./CheckOutPresenter";

const CheckOut = ({location, cartItems, currency }) => {

    const {isLoggedIn} = useRecoilValue(userState)
    const { pathname } = location;

    const [email, setEmail] = useState("");
    const [phone, setPhone] = useState("");
    const [userName, setUserName] = useState("");
    const [streetName, setStreetName] = useState("");
    const [apartment, setApartment] = useState("");
    const [postCode, setPostCode] = useState("");
    const [city, setCity] = useState("");
    const [country, setCountry] = useState("");
    const [addInfo, setAddInfo] = useState("");

return (
    <>
    { isLoggedIn ?  <CheckOutPresenter 
                                pathname={pathname}
                                cartItems = {cartItems}
                                currency = {currency}
                                email = {email}
                                phone = {phone}
                                userName = {userName}
                                streetName = {streetName}
                                apartment = {apartment}
                                postCode = {postCode}
                                city = {city}
                                country = {country}
                                addInfo = {addInfo}
                                setEmail = {setEmail}
                                setPhone = {setPhone}
                                setUserName = {setUserName}
                                setStreetName = {setStreetName}
                                setApartment = {setApartment}
                                setPostCode = {setPostCode}
                                setCity = {setCity}
                                setCountry = {setCountry}
                                setAddInfo = {setAddInfo}
                            /> : 
    
                            window.location.href = "/#/accounts/login"
    }
   </>
    
)

}

CheckOutPresenter.propTypes = {
    cartItems: PropTypes.array,
    currency: PropTypes.object,
    location: PropTypes.object
  };
  
  const mapStateToProps = state => {
    return {
      cartItems: state.cartData,
      currency: state.currencyData
    };
  };

export default connect(mapStateToProps)(CheckOut);


