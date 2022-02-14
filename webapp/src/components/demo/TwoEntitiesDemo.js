import React, { useState } from 'react';
import { useHistory } from 'react-router-dom'
import CreatableSelect from 'react-select/creatable';

import './TwoEntitiesDemo.css'
import { options } from '../../utils'


const TwoEntitiesDemo = () => {

    let history = useHistory()
    const [selectedEntity1, setSelectedEntity1] = useState({label: "earth", value: "earth"});
    const [selectedEntity2, setSelectedEntity2] = useState({label: "sun", value: "sun"});

    const onSubmit = () => {
        history.push(`/two-entities?entity1=${selectedEntity1.value}&entity2=${selectedEntity2.value}`)
    }

    return (
        <div className="two-entities-demo-container">
            <img src="" alt="Deleted for anonymity" className="logo" />
            <div className="two-entities-demo-selects-grid">
                <div>
                    <span className="mid-title">Entity 1</span>
                    <CreatableSelect
                        className="select"
                        value={options.find(obj => obj.value === selectedEntity1.value)}
                        onChange={setSelectedEntity1}
                        options={options}
                        placeholder={selectedEntity1.value}
                    />
                </div>
                <div>
                    <span className="mid-title">Entity 2</span>
                    <CreatableSelect
                        className="select"
                        value={options.find(obj => obj.value === selectedEntity2.value)}
                        onChange={setSelectedEntity2}
                        options={options}
                        placeholder={selectedEntity2.value}
                    />
                </div>
            </div>
            <div className="two-entities-demo-button">
                <button className="btn btn-primary" onClick={onSubmit}>Submit</button>
            </div>
        </div>
    );
}

export default TwoEntitiesDemo;
