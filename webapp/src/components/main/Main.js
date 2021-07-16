import React from 'react';
import { Link } from 'react-router-dom'

import SingleMapping from '../../assets/undraw_connection_b38q.svg'
import FullMapping from '../../assets/undraw_online_connection_6778.svg'
import TwoEntities from '../../assets/undraw_positive_attitude_xaae.svg'
import './Main.css'


const Main = () => {

    return (
        <div className="main-container">
            <span></span>
            <div className="demo-container">
                <Link to="/two-entities-demo" className="demo-links">
                    <img className="main-logo" src={TwoEntities} alt="logo" />
                    <div className="demo-title">
                        Two Entities
                    </div>
                    <div className="demo-description">
                        Visualization of two entities relations, based on GoogleAutosuggest, Quasimodo and ConceptNet.
                    </div>
                </Link>
            </div>
            
            <div className="demo-container">
                <Link to="/mapping-demo" className="demo-links">
                    <img className="main-logo" src={FullMapping} alt="logo" />
                    <div className="demo-title">
                        Full Mapping
                    </div>
                    <div className="demo-description">
                        Given a base domain and a target domain, it will visualize the mapping between entities from base to entities from target.
                    </div>
                </Link>
            </div>
            <div className="demo-container">
                <Link to="/single-mapping-demo" className="demo-links">
                    <img className="main-logo" src={SingleMapping} alt="logo" />
                    <div className="demo-title">
                        Single Mapping
                    </div>
                    <div className="demo-description">
                        Given two entities in base and two entities in target, it will make the mapping with all te information.
                    </div>
                </Link>
            </div>
            <span></span>
        </div>
    );
}

export default Main;
