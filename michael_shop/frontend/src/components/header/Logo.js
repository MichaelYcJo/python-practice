import PropTypes from "prop-types";
import React from "react";
import { Link } from "react-router-dom";
import { REACT_BACKEND_URL } from "utils/url";

const Logo = ({ imageUrl, logoClass }) => {
  return (
    <div className={`${logoClass ? logoClass : ""}`}>
      <Link to={process.env.PUBLIC_URL + "/"}>
        <img alt="" src={REACT_BACKEND_URL+ imageUrl} />
      </Link>
    </div>
  );
};

Logo.propTypes = {
  imageUrl: PropTypes.string,
  logoClass: PropTypes.string
};

export default Logo;
