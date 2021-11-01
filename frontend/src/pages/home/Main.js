import React, { Fragment } from "react";
import MetaTags from "react-meta-tags";
import Layout from "../../layouts/Layout";
import MainBanner from "wrappers/main-banner/MainBanner";
import TabProductList from "wrappers/product/TabProductList";
import BannerEleven from "../../wrappers/banner/BannerEleven";
import CountDownThree from "../../wrappers/countdown/CountDownThree";
import FeatureIconFour from "../../wrappers/feature-icon/FeatureIconFour";
import NewsletterThree from "../../wrappers/newsletter/NewsletterThree";

const Main = () => {
  return (
    <Fragment>
      <MetaTags>
        <title>Michael-Shop | Fashion Home</title>
        <meta
          name="description"
          content="Fashion home of Michael Shop react minimalist eCommerce template."
        />
      </MetaTags>
      <Layout
        headerContainerClass="container-fluid"
        headerPaddingClass="header-padding-2"
        headerTop="visible"
      >
        {/* hero slider */}
        <MainBanner />
        {/* tab product */}
        <TabProductList
          category="fashion"
          spaceBottomClass="pb-100"
          spaceTopClass="pt-100"
        />
        {/* banner */}
        <BannerEleven />
        {/* countdown */}
        <CountDownThree
          spaceTopClass="pt-100"
          spaceBottomClass="pb-100"
          dateTime="November 13, 2021 12:12:00"
          countDownImage="/assets/img/banner/deal-2.png"
        />
        {/* feature icon */}
        <FeatureIconFour
          bgImg="/assets/img/bg/shape.png"
          containerClass="container-fluid"
          gutterClass="padding-10-row-col"
          spaceTopClass="pt-50"
          spaceBottomClass="pb-40"
        />
        {/* newsletter */}
        <NewsletterThree
          spaceTopClass="pt-100"
          spaceBottomClass="pb-100"
          subscribeBtnClass="dark-red-subscribe"
        />
      </Layout>
    </Fragment>
  );
};

export default Main;
