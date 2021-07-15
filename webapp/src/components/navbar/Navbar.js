import React from 'react';
import { Link } from 'react-router-dom'
import './Navbar.css'


const Navbar = () => {

    return (
        <div className="navbar">
            <div className="left-side">
                <Link to="/" style={{textDecoration: 'none', color: 'whitesmoke'}}>
                    <i className="fas fa-home animate"></i>
                </Link> 
            </div>
        </div>
    );
}

export default Navbar;
