import { LoginAxiosInstance } from "api";
import PropTypes from "prop-types";
import React from "react";
import { connect } from "react-redux";
import { useRecoilValue, useSetRecoilState } from "recoil";
import {orderState, orderListSelector } from "recoil/orderRecoil";
import {
    addToCart,
    decreaseQuantity,
    cartItemStock,
    deleteFromCart,
    deleteAllFromCart
  } from "../../redux/actions/cartActions";
import OrderPresenter from "./OrderPresenter";

const Order = ({location, cartItems, currency}) => {
    
  const orders= useRecoilValue(orderListSelector);
  const setorders = useSetRecoilState(orderState);


  const deliveredConfirm = async (order_id) => {
    const order_data = {
          order_id
      }
      try {
          const { status, data } = await LoginAxiosInstance.put(
              `/orders/delivery/confirm`, order_data);
          if (status === 200) {
              setorders(data);
              return data;
          }
      }catch(e) {
          console.warn(e);
          return false;
      }
  }



  return (
    <OrderPresenter 
        location={location}
        cartItems={cartItems}
        cartItemStock = {cartItemStock}
        currency={currency}
        decreaseQuantity={decreaseQuantity}
        addToCart={addToCart}
        deleteFromCart={deleteFromCart}
        deleteAllFromCart={deleteAllFromCart}
        orders = {orders}
        deliveredConfirm = {deliveredConfirm}
    />
  );
};

Order.propTypes = {
  currency: PropTypes.object,
  location: PropTypes.object,
};

const mapStateToProps = state => {
  return {
    cartItems: state.cartData,
    currency: state.currencyData
  };
};

const mapDispatchToProps = dispatch => {
  return {
    addToCart: (item, addToast, quantityCount) => {
      dispatch(addToCart(item, addToast, quantityCount));
    },
    decreaseQuantity: (item, addToast) => {
      dispatch(decreaseQuantity(item, addToast));
    },
    deleteFromCart: (item, addToast) => {
      dispatch(deleteFromCart(item, addToast));
    },
    deleteAllFromCart: addToast => {
      dispatch(deleteAllFromCart(addToast));
    }
  };
};

export default connect(mapStateToProps, mapDispatchToProps)(Order);
