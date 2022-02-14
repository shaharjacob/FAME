import React, { useState } from 'react';
import CreatableSelect from 'react-select/creatable';
import { useHistory } from 'react-router-dom'
import { options } from '../../utils'
import './SingleMappingDemo.css'
import RightArrow from '../../assets/arrow-right.svg'


const SingleMappingDemo = () => {

    let history = useHistory()
    const [selectedBase1, setSelectedBase1] = useState({label: "earth", value: "earth"});
    const [selectedBase2, setSelectedBase2] = useState({label: "sun", value: "sun"});
    const [selectedTarget1, setSelectedTarget1] = useState({label: "electrons", value: "electrons"});
    const [selectedTarget2, setSelectedTarget2] = useState({label: "nucleus", value: "nucleus"});

    const onSelectSuggestion = (base1, base2, target1, target2) => {
        setSelectedBase1({label: base1, value: base1})
        setSelectedBase2({label: base2, value: base2})
        setSelectedTarget1({label: target1, value: target1})
        setSelectedTarget2({label: target2, value: target2})
    }

    const onSubmitBipartite = () => {
        history.push(`/bipartite?base1=${selectedBase1.value}&base2=${selectedBase2.value}&target1=${selectedTarget1.value}&target2=${selectedTarget2.value}`)
    }

    const onSubmitClustering = () => {
        history.push(`/cluster?base1=${selectedBase1.value}&base2=${selectedBase2.value}&target1=${selectedTarget1.value}&target2=${selectedTarget2.value}`)
    }

    const onSubmitBoth = () => {
        history.push(`/single-mapping?base1=${selectedBase1.value}&base2=${selectedBase2.value}&target1=${selectedTarget1.value}&target2=${selectedTarget2.value}`)
    }

    return (
        <div className="single-mapping-demo-container">
            <img src="" alt="Deleted for anonymity" className="logo" />
            <div className="single-mapping-demo-selects-grid">
                <div>
                    <span className="mid-title">Base 1</span>
                    <CreatableSelect
                        className="select"
                        value={options.find(obj => obj.value === selectedBase1.value)}
                        onChange={setSelectedBase1}
                        options={options}
                        placeholder={selectedBase1.value}
                    />
                </div>

                <div>
                    <span className="mid-title">Target 1</span>
                    <CreatableSelect
                        className="select"
                        value={options.find(obj => obj.value === selectedTarget1.value)}
                        onChange={setSelectedTarget1}
                        options={options}
                        placeholder={selectedTarget1.value}
                    />
                </div>

                <div>
                    <span className="mid-title">Base 2</span>
                    <CreatableSelect
                        className="select"
                        value={options.find(obj => obj.value === selectedBase2.value)}
                        onChange={setSelectedBase2}
                        options={options}
                        placeholder={selectedBase2.value}
                    />
                </div>

                <div>
                    <span className="mid-title">Target 2</span>
                    <CreatableSelect
                        className="select"
                        value={options.find(obj => obj.value === selectedTarget2.value)}
                        onChange={setSelectedTarget2}
                        options={options}
                        placeholder={selectedTarget2.value}
                    />
                </div>
            </div>
            <div className="single-mapping-demo-button">
                <button className="btn btn-primary" onClick={onSubmitClustering}>Clustring</button>
                &nbsp;&nbsp;&nbsp;&nbsp;
                <button className="btn btn-primary" onClick={onSubmitBipartite}>Bipartite</button>
                &nbsp;&nbsp;&nbsp;&nbsp;
                <button className="btn btn-primary" onClick={onSubmitBoth}>Both</button>
            </div>
            <div className="suggestions">
                <b><u>Suggestions:</u></b><br/>
                <ul>
                    <b>Good:</b>
                    <ul>
                        <li>
                            <button className="suggestion-button" onClick={() => onSelectSuggestion("earth", "sun", "electrons", "nucleus")}>
                                (earth&nbsp;&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;&nbsp;sun)
                                &nbsp;&nbsp; &nbsp;&nbsp;~ &nbsp;&nbsp; &nbsp;&nbsp;
                                (electrons&nbsp;&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;&nbsp;nucleus)
                            </button>
                        </li>
                        <li>
                            <button className="suggestion-button" onClick={() => onSelectSuggestion("singer", "songs", "programmer", "code")}>
                                (singer&nbsp;&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;&nbsp;songs)
                                &nbsp;&nbsp; &nbsp;&nbsp;~ &nbsp;&nbsp; &nbsp;&nbsp;
                                (programmer&nbsp;&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;&nbsp;code)
                            </button>
                        </li>
                        <li>
                            <button className="suggestion-button" onClick={() => onSelectSuggestion("cars", "road", "boats", "lake")}>
                                (cars&nbsp;&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;&nbsp;road)
                                &nbsp;&nbsp; &nbsp;&nbsp;~ &nbsp;&nbsp; &nbsp;&nbsp;
                                (boats&nbsp;&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;&nbsp;lake)
                            </button>
                        </li>   
                        <li>
                            <button className="suggestion-button" onClick={() => onSelectSuggestion("thoughts", "brain", "astronaut", "space")}>
                                (thoughts&nbsp;&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;&nbsp;brain)
                                &nbsp;&nbsp; &nbsp;&nbsp;~ &nbsp;&nbsp; &nbsp;&nbsp;
                                (astronaut&nbsp;&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;&nbsp;space)
                            </button>
                        </li>
                        <li>
                            <button className="suggestion-button" onClick={() => onSelectSuggestion("sunscreen", "sun", "umbrella", "rain")}>
                                (sunscreen&nbsp;&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;&nbsp;sun)
                                &nbsp;&nbsp; &nbsp;&nbsp;~ &nbsp;&nbsp; &nbsp;&nbsp;
                                (umbrella&nbsp;&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;&nbsp;rain)
                            </button>
                        </li>
                        <li>
                            <button className="suggestion-button" onClick={() => onSelectSuggestion("student", "homework", "citizen", "duties")}>
                                (student&nbsp;&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;&nbsp;homework)
                                &nbsp;&nbsp; &nbsp;&nbsp;~ &nbsp;&nbsp; &nbsp;&nbsp;
                                (citizen&nbsp;&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;&nbsp;duties)
                            </button>
                        </li>
                    </ul>
                    
                    <b>Bad:</b>
                    <ul>
                        <li>
                            <button className="suggestion-button" onClick={() => onSelectSuggestion("medicine", "illness", "law", "anarchy")}>
                                (medicine&nbsp;&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;&nbsp;illness)
                                &nbsp;&nbsp; &nbsp;&nbsp;~ &nbsp;&nbsp; &nbsp;&nbsp;
                                (law&nbsp;&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;&nbsp;anarchy)
                            </button>
                        </li>
                        <li>
                            <button className="suggestion-button" onClick={() => onSelectSuggestion("plant", "desert", "cat", "street")}>
                                (plant&nbsp;&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;&nbsp;desert)
                                &nbsp;&nbsp; &nbsp;&nbsp;~ &nbsp;&nbsp; &nbsp;&nbsp;
                                (cat&nbsp;&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;&nbsp;street)
                            </button>
                        </li>
                        <li>
                            <button className="suggestion-button" onClick={() => onSelectSuggestion("air conditioner", "summer", "heater", "winter")}>
                                (air conditioner&nbsp;&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;&nbsp;summer)
                                &nbsp;&nbsp; &nbsp;&nbsp;~ &nbsp;&nbsp; &nbsp;&nbsp;
                                (heater&nbsp;&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;&nbsp;winter)
                            </button>
                        </li>
                    </ul>
                </ul>
            </div>
        </div>
    );
}

export default SingleMappingDemo;
