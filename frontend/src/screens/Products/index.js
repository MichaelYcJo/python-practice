import React from 'react'
import styled from "styled-components";
import { popularProducts } from "data";
import Product from "./Product";
import SideFilter from './SideFilter';


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


const Products = () => {
  return (
    <>
    <SectionHeader>Header</SectionHeader>
    <SideFilter />
    <Container>
      {popularProducts.map((item) => (
        <Product item={item} key={item.id} />
      ))}
    </Container>
    </>
  );
};

export default Products;
