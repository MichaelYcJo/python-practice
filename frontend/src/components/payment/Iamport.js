import AxiosInstance, { LoginAxiosInstance } from 'api';
import React, { useEffect} from 'react';


var order_id;

const Iamport = (order_data) => {

    useEffect(() => {
        const jquery = document.createElement('script');
        jquery.src = 'https://code.jquery.com/jquery-1.12.4.min.js';
        const iamport = document.createElement('script');
        iamport.src = 'https://cdn.iamport.kr/js/iamport.payment-1.1.7.js';
        document.head.appendChild(jquery);
        document.head.appendChild(iamport);

        return () => {
            document.head.removeChild(jquery);
            document.head.removeChild(iamport);
        }

}, [])


  const onSubmitIamport = async (e) => {
      e.preventDefault();

    if(!order_data.userName || !order_data.apartment || !order_data.city
        || !order_data.email || !order_data.streetName || !order_data.postCode
        || !order_data.phone || !order_data.country ) {
        alert('주문정보를 모두 작성해주세요');
        return false;
    }
    if(order_data.cartItems.length === 0 || !order_data.totalPrice) {
        alert('주문정보가 잘못되었습니다')
        window.location('/');
    }


    const {IMP} = window;
    IMP.init('imp56366274');

    const order_json_data = {
            merchant_uid: `mid_${new Date().getTime()}`,
            pay_method: 'card',
            amount: order_data.totalPrice,
            name: `${order_data.userName}의 결제`,
            buyer_name: order_data.userName,
            buyer_email: order_data.email,
            buyer_tel : order_data.phone,
            apartment : order_data.apartment,
            city : order_data.city,
            street_name : order_data.streetName,
            post_code : order_data.postCode,
            country : order_data.country,
            additional_message : order_data.addInfo,
            cartItems: order_data.cartItems
        
    }

    try {
        const { status, data } = await LoginAxiosInstance.post(
            '/orders/checkout', order_json_data);
        if (status === 200) {
            order_id = data.order_id;
        }
    }catch(err) {
        alert(err.message)
        return false;
    }


    IMP.request_pay(order_json_data, callback);
    }


    const callback = async (response) => {
        const {success, error_msg, imp_uid, pay_method, paid_amount, status} = response
        if (success) {
            response.order_id = order_id;
            try {
                const { status, data } = await AxiosInstance.post(
                    '/orders/checkout/complate', response);
                if (status === 200) {
                    alert('결제성공')
                    window.location.href = '/';
                }
            }catch(err) {
                alert(err.message)
                return false;
            }

        } else {
            alert(error_msg);
        }

    }

    return (
        <button type='submit' className="btn-hover" onClick={onSubmitIamport} >Place Order</button>
    )

}

export default Iamport;