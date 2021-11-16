import React, { Fragment, useState } from "react";
import { Link } from "react-router-dom";
import { useToasts } from "react-toast-notifications";
import MetaTags from "react-meta-tags";
import { BreadcrumbsItem } from "react-breadcrumbs-dynamic";
import { getDiscountPrice } from "utils/product";
import LayoutOne from "../../layouts/LayoutOne";
import Breadcrumb from "../../wrappers/breadcrumb/Breadcrumb";
import { REACT_BACKEND_URL } from "utils/url";

const OrderPresenter = ({
  location,
  orders,
  deliveredConfirm
}) => {

  const { addToast } = useToasts();
  const { pathname } = location;

  return (
    <Fragment>
      <MetaTags>
        <title>Michael-Shop | Order</title>
        <meta
          name="description"
          content="Cart page of Michael-Shop react minimalist eCommerce template."
        />
      </MetaTags>

      <BreadcrumbsItem to={process.env.PUBLIC_URL + "/"}>Home</BreadcrumbsItem>
      <BreadcrumbsItem to={process.env.PUBLIC_URL + pathname}>
        Order
      </BreadcrumbsItem>

      <LayoutOne headerTop="visible">
        {/* breadcrumb */}
        <Breadcrumb />
        <div className="cart-main-area pt-90 pb-100">
          <div className="container">
            {orders && orders.length >= 1 ? (
              <Fragment>
                <h3 className="cart-page-title">Your Orders</h3>
                <div className="row">
                  <div className="col-12">
                    <div className="table-content table-responsive cart-table-content">
                      <table>
                        <thead>
                          <tr>
                            <th>Product Name</th>
                            <th>Qty</th>
                            <th>Subtotal</th>
                            <th>action</th>
                          </tr>
                        </thead>
                        <tbody>
                          {orders.map((orderObject, key) => {
                           
                            return (
                              <tr key={key}>

                                <td className="product-name padding-custom">
                                  {orderObject.order_items.map((product, key) => {
                                    return(
                                      <p key={`product-${key}-${(Math.random() *1000) + 1}`}>
                                        <Link 
                                                to={
                                                  process.env.PUBLIC_URL +
                                                  product.product.url_path +
                                                  product.product.pk
                                                }
                                              >
                                          {product.product.name}
                                        </Link>
                                      </p>
                                  )})
                                  }             
                                </td>

                                <td className="product-quantity padding-custom">
                                {orderObject.order_items.map((product, key) => {
                                    return(
                                      <p key={`qty-${product.product.name}-${key}-${(Math.random() *1000) + 1}`}>
                                         X {product.qty}
                                      </p>
                                  )})
                                  }         

                                </td>
                                <td className="product-subtotal padding-custom">
                                  ₩{
                                    (orderObject.total_price).toFixed(2)
                                    }
                                </td>

                                <td className="product-remove padding-custom">
                                  {orderObject.is_delivered ?
                                    <p>배송완료</p>
                                :                                   
                                 <button className="btn-hover"
                                style={{backgroundColor: "whitesmoke"}}
                                onClick={() =>
                                  deliveredConfirm(orderObject.pk)
                                }
                              >
                               구매확정
                              </button> }
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  </div>
                </div>

              </Fragment>
            ) : (
              <div className="row">
                <div className="col-lg-12">
                  <div className="item-empty-area text-center">
                    <div className="item-empty-area__icon mb-30">
                      <i className="pe-7s-cart"></i>
                    </div>
                    <div className="item-empty-area__text">
                      No items found in order <br />{" "}
                      <Link to={process.env.PUBLIC_URL + "/shop-grid-standard"}>
                        Shop Now
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </LayoutOne>
    </Fragment>
  );
};

export default (OrderPresenter);
