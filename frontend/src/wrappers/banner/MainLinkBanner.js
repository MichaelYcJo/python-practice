import PropTypes from "prop-types";
import React from "react";
import bannerData from "../../data/banner/main-shop-link.json";
import BannerSingle from "../../components/banner/BannerSingle.js";

const MainLinkBanner = ({ spaceBottomClass }) => {
  return (
    <div className={`banner-area ${spaceBottomClass ? spaceBottomClass : ""}`}>
      <div className="row no-gutters">
        {bannerData &&
          bannerData.map((single, key) => {
            return <BannerSingle data={single} key={key} />;
          })}
      </div>
    </div>
  );
};

MainLinkBanner.propTypes = {
  spaceBottomClass: PropTypes.string
};

export default MainLinkBanner;
