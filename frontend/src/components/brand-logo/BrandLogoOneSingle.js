import PropTypes from "prop-types";
import React from "react";
import { REACT_BACKEND_URL } from "utils/url";

const BrandLogoOneSingle = ({ data, sliderClassName, spaceBottomClass }) => {
  return (
    <div
      className={`single-brand-logo ${sliderClassName ? sliderClassName : ""} ${
        spaceBottomClass ? spaceBottomClass : ""
      }`}
    >
      <img src={REACT_BACKEND_URL + data.image} alt="" />
    </div>
  );
};

BrandLogoOneSingle.propTypes = {
  data: PropTypes.object,
  sliderClassName: PropTypes.string,
  spaceBottomClass: PropTypes.string
};

export default BrandLogoOneSingle;
