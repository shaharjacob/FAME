import React from 'react';
import { useHistory } from 'react-router-dom'
import Logo from '../../assets/mapping-entities-hayadata.png'
import './MappingDemo.css'


const MappingDemo = () => {

    let history = useHistory()

    const onSubmit = () => {
        var base = document.getElementById("base-input")
        var target = document.getElementById("target-input")
        history.push(`/mapping?base=${base.value.split(",")}&target=${target.value.split(",")}`)
    }

    return (
        <div className="mapping-demo-container">
            <img style={{width: "400px", marginTop: '100px'}} src={Logo} alt="logo" />
            <div className="mapping-demo-inputs">
                <span><i className="fas fa-home text-blue"></i>&nbsp;Base entities</span>
                <span><i class="fas fa-dot-circle text-red"></i>&nbsp;Target entities</span>
                <textarea classNamea="mapping-demo-textarea" id="base-input" />
                <textarea className="mapping-demo-textarea" id="target-input" />
            </div>
            <button className="mapping-demo-button-submit" onClick={onSubmit}>Submit</button>
        </div>
    );
}

export default MappingDemo;
