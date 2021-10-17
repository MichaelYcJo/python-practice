import PropTypes from "prop-types";
import React from "react";
import RegisterPresenter from "pages/auth/Register/RegisterPresenter";

const Regitser = () => {

  return (
      <RegisterPresenter />
   
  );
};

Regitser.propTypes = {
  location: PropTypes.object
};

export default Regitser;




