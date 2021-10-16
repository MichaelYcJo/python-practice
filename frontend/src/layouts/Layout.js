import PropTypes from "prop-types";
import React, { Fragment } from "react";
import LayoutHeader from "../wrappers/header/LayoutHeader";
import FooterOne from "../wrappers/footer/FooterOne";

const Layout = ({ children }) => {
  return (
    <Fragment>
      <HeaderSix layout="container-fluid" />
      {children}
      <FooterOne spaceTopClass="pt-100" spaceBottomClass="pb-70" />
    </Fragment>
  );
};

export default Layout;

Layout.propTypes = {
  children: PropTypes.any
};
