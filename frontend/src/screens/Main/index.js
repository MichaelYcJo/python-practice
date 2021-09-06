import React from 'react'

import { MainContainer, MainContent, MainItems, MainH1, MainP, MainBtn } from 'screens/Main/MainContainer'
import MainBackground from 'assets/videos/MainBackground.mp4'

import Products from 'screens/Products';
import { productData, productDataTwo } from 'screens/Products/data';
import Feature from 'screens/Feature';
import Footer from 'screens/Footer';

export default function Main() {

    return (
        <MainContainer>
            <MainContent>
                <MainItems>
                    <video muted autoPlay loop>
                        <source src={MainBackground} type="video/mp4" />
                    </video>
                    <MainH1>Find Your Style</MainH1>
                    <MainP>Attractive Ever</MainP>
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
