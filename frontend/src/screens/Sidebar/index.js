import React from 'react';
import {
    SidebarContainer,
    Icon,
    CloseIcon,
    SidebarMenu,
    SidebarLink,
    //SidebarRoute,
    //SideBtnWrap,
    AuthWrap,
    LoginRoute,
    RegisterRoute
} from 'screens/Sidebar/SidebarContainer';

const Sidebar = ({ isOpen, toggle }) => {
    return (
        <SidebarContainer isOpen={isOpen} onClick={toggle}>
            <Icon onClick={toggle}>
                <CloseIcon />
            </Icon>
            <SidebarMenu>
                <SidebarLink to='/'>New Releases</SidebarLink>
                <SidebarLink to='/'>Men</SidebarLink>
                <SidebarLink to='/'>Women</SidebarLink>
            </SidebarMenu>
            <AuthWrap>
                <RegisterRoute to='/'>Register</RegisterRoute>
                <LoginRoute to='/accounts/login'>Log In</LoginRoute>
            </AuthWrap>

            {/*<SideBtnWrap>
                <SidebarRoute to='/'>Order Now</SidebarRoute>
            </SideBtnWrap> */}

        </SidebarContainer>
    );
};

export default Sidebar;