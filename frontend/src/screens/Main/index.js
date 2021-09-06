import React from 'react'

import { MainContainer, MainContent, MainItems, MainH1, MainP, MainBtn } from 'screens/Main/MainContainer'


import Products from 'screens/Products';
import { productData, productDataTwo } from 'screens/Products/data';
import Feature from 'screens/Feature';
import Footer from 'screens/Footer';

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
