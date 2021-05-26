import React, { useState } from 'react';
import Select from 'react-select'
import { useHistory } from 'react-router-dom'
import { options } from '../../utils'
import './Main.css'


const Main = () => {

    let history = useHistory()
    const [selectedEdge1Head, setSelectedEdge1Head] = useState({label: "earth", value: "earth"});
    const [selectedEdge1Tail, setSelectedEdge1Tail] = useState({label: "sun", value: "sun"});
    const [selectedEdge2Head, setSelectedEdge2Head] = useState({label: "electrons", value: "electrons"});
    const [selectedEdge2Tail, setSelectedEdge2Tail] = useState({label: "nucleus", value: "nucleus"});

    const onSubmit = () => {
        history.push(`/bipartite?head1=${selectedEdge1Head.value}&tail1=${selectedEdge1Tail.value}&head2=${selectedEdge2Head.value}&tail2=${selectedEdge2Tail.value}`)
    }

    return (
        <div className="main-container">
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
                <button className="btn btn-primary" onClick={onSubmit}>Sumbit</button>
            </div>
        </div>
    );
}

export default Main;
