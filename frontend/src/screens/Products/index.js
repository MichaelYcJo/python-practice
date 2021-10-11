import axiosInstance from 'api';
import React, { useEffect } from 'react'
import { useRecoilState } from 'recoil';
import { productState } from 'recoil/productRecoil';

import ProductPresenger from './ProductPresenter';

export default function Products({location}) {
  const [products, setProduct] = useRecoilState(productState)

  
  useEffect(() => {
    const {search}  = location;
  
    axiosInstance.get(
      `/products/list${search}`, )
      .then(response => {
        setProduct(response.data.results)
      })
      .catch(err => {
        console.log(err)
      })
    }, [location, setProduct])

  return (
    <>
      <ProductPresenger products={products} />
    </>
  );
};


