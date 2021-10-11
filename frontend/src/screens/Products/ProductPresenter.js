
import React from 'react'
import Product from "./Product";
import SideFilter from './SideFilter';

import { useRecoilState } from 'recoil';

import styled from "styled-components";


const Container = styled.div`
    padding: 20px;
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
`;

const SectionHeader = styled.h1`
  color: #fff;
  height: 10%;
  font-size: 2rem;
  padding : 40px 48px 30px 48px;
`;


export default function ProductPresenger({products}) {

    return (
      <>
    <SectionHeader>Header</SectionHeader>
    <SideFilter />
    <Container>
      {products.map(product => (
        <Product key={product.pk} product={product} />
      ))}
    </Container>
            
        </>
    )
}
