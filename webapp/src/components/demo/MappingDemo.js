import React from 'react';
import { useHistory } from 'react-router-dom'
import Logo from '../../assets/mapping-entities-hayadata.png'
import './MappingDemo.css'


const MappingDemo = () => {

    let history = useHistory()

    const onSubmit = () => {
        var base = document.getElementById("base-input")
        var target = document.getElementById("target-input")
        var depth = document.getElementById("depth")
        var top_solutions = document.getElementById("top-solutions")
        var suggestions = document.getElementById("suggestions")
        var algo = document.getElementById("algo")
        history.push(`/mapping?base=${base.value.split(",")}&target=${target.value.split(",")}&depth=${depth.value}&top=${top_solutions.value}&suggestions=${suggestions.value}&algo=${algo.value}`)
    }

    return (
        <div className="mapping-demo-container">
            <img style={{width: "400px", marginTop: '100px'}} src={Logo} alt="logo" />
            <div className="mapping-demo-inputs">
                <span><i className="fas fa-home text-blue"></i>&nbsp;Base entities</span>
                <span><i className="fas fa-dot-circle text-red"></i>&nbsp;Target entities</span>
                <textarea classNamea="mapping-demo-textarea" id="base-input" />
                <textarea className="mapping-demo-textarea" id="target-input" />
            </div>
            <div className="mapping-demo-args">
                <span><i className="fas fa-skull-crossbones dark-gray"></i>&nbsp;Depth</span>
                <span><i className="fas fa-trophy gold"></i>&nbsp;Top solutions</span>
                <span><i className="far fa-lightbulb gold"></i>&nbsp;Number of Suggestions</span>
                <span><i className="fas fa-play green"></i>&nbsp;Algorithm</span>
                <input className="mapping-demo-input" defaultValue={4} id="depth" />
                <input className="mapping-demo-input" defaultValue={3} id="top-solutions" />
                <input className="mapping-demo-input" defaultValue={3} id="suggestions" />
                <input className="mapping-demo-input" defaultValue="beam" id="algo" placeholder="beam / dfs" />
            </div>
            <button className="mapping-demo-button-submit" onClick={onSubmit}>Submit</button>
        </div>
    );
}

export default MappingDemo;
