import React, { useState } from 'react';
import Select from 'react-select'
import { useHistory } from 'react-router-dom'
import { options } from '../../utils'
import './Main.css'
import RightArrow from '../../assets/arrow-right.svg'
import Hayadata from '../../assets/hayadata.png'


const Main = () => {

    let history = useHistory()
    const [selectedEdge1Head, setSelectedEdge1Head] = useState({label: "earth", value: "earth"});
    const [selectedEdge1Tail, setSelectedEdge1Tail] = useState({label: "sun", value: "sun"});
    const [selectedEdge2Head, setSelectedEdge2Head] = useState({label: "electrons", value: "electrons"});
    const [selectedEdge2Tail, setSelectedEdge2Tail] = useState({label: "nucleus", value: "nucleus"});

    const onSelectSuggestion = (head1, tail1, head2, tail2) => {
        setSelectedEdge1Head({label: head1, value: head1})
        setSelectedEdge1Tail({label: tail1, value: tail1})
        setSelectedEdge2Head({label: head2, value: head2})
        setSelectedEdge2Tail({label: tail2, value: tail2})
    }

    const onSubmitBipartite = () => {
        history.push(`/bipartite?head1=${selectedEdge1Head.value}&tail1=${selectedEdge1Tail.value}&head2=${selectedEdge2Head.value}&tail2=${selectedEdge2Tail.value}`)
    }

    const onSubmitClustering = () => {
        history.push(`/cluster?head1=${selectedEdge1Head.value}&tail1=${selectedEdge1Tail.value}&head2=${selectedEdge2Head.value}&tail2=${selectedEdge2Tail.value}`)
    }

    const onSubmitBoth = () => {
        history.push(`/full?head1=${selectedEdge1Head.value}&tail1=${selectedEdge1Tail.value}&head2=${selectedEdge2Head.value}&tail2=${selectedEdge2Tail.value}`)
    }

    return (
        <div className="main-container">
            <img src={Hayadata} alt="logo" className="logo" />
            <div className="main-selects-grid">
                <span className="title">
                    Edge 1
                </span>

                <span className="title">
                    Edge 2
                </span>

                <div>
                    <span className="mid-title">Head</span>
                    <Select
                        className="select"
                        value={options.find(obj => obj.value === selectedEdge1Head.value)}
                        onChange={setSelectedEdge1Head}
                        options={options}
                        placeholder={selectedEdge1Head.value}
                    />
                </div>

                <div>
                    <span className="mid-title">Head</span>
                    <Select
                        className="select"
                        value={options.find(obj => obj.value === selectedEdge2Head.value)}
                        onChange={setSelectedEdge2Head}
                        options={options}
                        placeholder={selectedEdge2Head.value}
                    />
                </div>

                <div>
                    <span className="mid-title">Tail</span>
                    <Select
                        className="select"
                        value={options.find(obj => obj.value === selectedEdge1Tail.value)}
                        onChange={setSelectedEdge1Tail}
                        options={options}
                        placeholder={selectedEdge1Tail.value}
                    />
                </div>

                <div>
                    <span className="mid-title">Tail</span>
                    <Select
                        className="select"
                        value={options.find(obj => obj.value === selectedEdge2Tail.value)}
                        onChange={setSelectedEdge2Tail}
                        options={options}
                        placeholder={selectedEdge2Tail.value}
                    />
                </div>
            </div>
            <div className="main-button">
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
                            <button className="suggestion-button" onClick={() => onSelectSuggestion("student", "homework", "civizen", "duties")}>
                                (student&nbsp;&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;&nbsp;homework)
                                &nbsp;&nbsp; &nbsp;&nbsp;~ &nbsp;&nbsp; &nbsp;&nbsp;
                                (civizen&nbsp;&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;&nbsp;duties)
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

export default Main;
