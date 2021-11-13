import PropTypes from "prop-types";
import React from "react";
import { Link } from "react-router-dom";
import { REACT_BACKEND_URL } from "utils/url";

const BannerSingle = ({ data, spaceBottomClass }) => {
  const HandleClick = (e) => {
    e.preventDefault();
    alert('comming soon')
  }

  return (
    <div className="col-lg-6 col-md-6">
      <div
        className={`single-banner-2 ${
          spaceBottomClass ? spaceBottomClass : ""
        } ${data.textAlign === "right" ? "align_right" : ""}`}
      >
        <Link to={process.env.PUBLIC_URL + data.link}>
          <img className="banner-link-image" src={REACT_BACKEND_URL + data.image} alt="" />
        </Link>
        <div className="banner-content-2 banner-content-2--style2">
          <h3>{data.title}</h3>
          <h4>
            {data.subtitle} <span>{data.price}</span>
          </h4>
          {data.link === '/men/clothes/list' ?
            <Link to={process.env.PUBLIC_URL + data.link}>
              <i className="fa fa-long-arrow-right" />
            </Link>
        :  
            <Link to={process.env.PUBLIC_URL + data.link} onClick={HandleClick}>
              <i className="fa fa-long-arrow-right" />
            </Link>
        }
        </div>
      </div>
    </div>
  );
};

BannerSingle.propTypes = {
  data: PropTypes.object,
  spaceBottomClass: PropTypes.string
};

export default BannerSingle;
