import React from 'react'
import Navbar from 'components/Navbar'
import { MainContainer, MainContent, MainItems, MainH1, MainP, MainBtn } from 'components/Main/MainElements'


export default function Main() {
    return (
        <MainContainer>
            <Navbar />
            <MainContent>
                <MainItems>
                    <MainH1>Attractive Ever</MainH1>
                    <MainP>It's Real</MainP>
                    <MainBtn>Click</MainBtn>
                </MainItems>
            </MainContent>
        </MainContainer>
    )
}
