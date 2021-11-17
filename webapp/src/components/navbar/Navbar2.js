import React from 'react';
import { Link } from 'react-router-dom'
import './Navbar.css'
import HyadataLab from '../../assets/hyadata_without_text.png'


const Navbar2 = () => {

    return (
        <div className="navbar2">
            <div className="left-side">
                <Link to="/" style={{textDecoration: 'none'}}>
                    <img className="animate" style={{paddingBottom: "5px", paddingLeft: "5px", paddingRight: "5px"}} width="50px" src={HyadataLab} alt="HyadataLab" />
                    <span className="auto-sme">autoSME</span>
                </Link> 
            </div>
            <div className="right-side">
                Explore
            </div>
        </div>
    );
}

export default Navbar2;
