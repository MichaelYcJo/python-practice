
import React from 'react';
import { Nav, NavLink, NavIcon, Bars } from './NavbarContainer';

const Navbar = ({ toggle }) => {
    return (
        <>
            <Nav>
                <NavLink to='/'>Michael-Shop</NavLink>
                <NavIcon onClick={toggle}>
                    <p>Menu</p>
                    <Bars />
                </NavIcon>
            </Nav>
        </>
    );
};

export default Navbar;