import PropTypes from "prop-types";
import React from "react";
import { Link } from "react-router-dom";
import { REACT_BACKEND_URL } from "utils/url";

const MainBannerSwiperContent = ({ data, sliderClass }) => {
  return (
    <div
      className={`single-slider-2 slider-height-2 d-flex align-items-center bg-img ${
        sliderClass ? sliderClass : ""
      }`}
      style={{ backgroundImage: `url(${REACT_BACKEND_URL + data.image})` }}
    >
      <div className="container">
        <div className="row">
          <div className="col-xl-6 col-lg-7 col-md-8 col-12 ml-auto">
            <div className="slider-content-2 slider-animated-1">
              <h3 className="animated no-style text-light">{data.title}</h3>
              <h1
                className="animated text-light"
                dangerouslySetInnerHTML={{ __html: data.subtitle }}
              />
              <div className="slider-btn btn-hover">
                <Link
                  className="animated rounden-btn"
                  to={process.env.PUBLIC_URL + data.url}
                >
                  SHOP NOW
                </Link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

MainBannerSwiperContent.propTypes = {
  data: PropTypes.object,
  sliderClass: PropTypes.string
};

export default MainBannerSwiperContent;
