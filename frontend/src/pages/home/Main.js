import React, {useEffect, Fragment } from "react";
import MetaTags from "react-meta-tags";
import Layout from "../../layouts/Layout";
import MainBanner from "wrappers/main-banner/MainBanner";
import TabProductList from "wrappers/product/TabProductList";
import MainLinkBanner from "wrappers/banner/MainLinkBanner";
import MainCountDown from "wrappers/countdown/MainCountDown";
import MainFeatureIcon from "wrappers/feature-icon/MainFeatureIcon";
import Newsletter from "wrappers/newsletter/Newsletter";

import { categoryState, productListSelector } from "recoil/productRecoil";
import { useRecoilValue, useSetRecoilState } from "recoil";

const Main = () => {
  const products = useRecoilValue(productListSelector);
  const productCategory = useSetRecoilState(categoryState);

  useEffect(() => {
    productCategory('main')
  }, [productCategory])

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
          products = {products}
        />
        {/* banner */}
        <MainLinkBanner />
        {/* countdown */}
        <MainCountDown
          spaceTopClass="pt-100"
          spaceBottomClass="pb-100"
          dateTime="November 13, 2023 12:12:00"
          countDownImage="/media/main/main-bag.jpeg"
        />
        {/* feature icon */}
        <MainFeatureIcon
          bgImg="/media/img/bg/shape.png"
          containerClass="container-fluid"
          gutterClass="padding-10-row-col"
          spaceTopClass="pt-50"
          spaceBottomClass="pb-40"
        />
        {/* Todo: newsletter 
        <Newsletter
          spaceTopClass="pt-100"
          spaceBottomClass="pb-100"
          subscribeBtnClass="dark-red-subscribe"
        />
        */}
      </Layout>
    </Fragment>
  );
};

export default Main;
