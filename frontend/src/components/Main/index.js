import React from 'react'

import { MainContainer, MainContent, MainItems, MainH1, MainP, MainBtn } from 'components/Main/MainElements'


import Products from 'components/Products';
import { productData, productDataTwo } from 'components/Products/data';
import Feature from 'components/Feature';
import Footer from 'components/Footer';

export default function Main() {

    return (
        <MainContainer>
            <MainContent>
                <MainItems>
                    <MainH1>Attractive Ever</MainH1>
                    <MainP>It's Real</MainP>
                    <MainBtn>Click</MainBtn>
                </MainItems>
            </MainContent>
            <Products heading='Choose your favorite' data={productData} />
            <Feature />
            <Products heading='Recommand for You' data={productDataTwo} />
            <Footer />
        </MainContainer>
    )
}
