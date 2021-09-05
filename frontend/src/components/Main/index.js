import React, { useState } from 'react'
import Navbar from 'components/Navbar'
import { MainContainer, MainContent, MainItems, MainH1, MainP, MainBtn } from 'components/Main/MainElements'
import Sidebar from 'components/Sidebar'


export default function Main() {
    const [isOpen, setIsOpen] = useState(false);
    const toggle = () => {
        setIsOpen(!isOpen);
    }
    return (
        <MainContainer>
            <Navbar toggle={toggle} />
            <Sidebar isOpen={isOpen} toggle={toggle} />
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
