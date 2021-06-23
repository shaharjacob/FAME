import cloneDeep from 'lodash/cloneDeep'
import React from 'react'

import './Graph.css'
import { IsEmpty } from '../../utils'
import RightArrow from '../../assets/arrow-right.svg'

const Descriptor = ({data, setGraph, setGraphSelect, setOptions, scores, distThreshold, base1, setCurrBase1, base2, setCurrBase2, 
                    target1, setCurrTarget1, target2, setCurrTarget2, similarityThreshold, noMatchFound, setNoMatchFound}) => {

    const onGraphClick = (newGraph, entity1, entity2, entity3, entity4) => {
        setCurrBase1(entity1) 
        setCurrBase2(entity2) 
        setCurrTarget1(entity3) 
        setCurrTarget2(entity4)
        setGraphSelect(newGraph)
        if (!IsEmpty(data[newGraph][distThreshold]["graph"])) {
            let copyGraph = cloneDeep(data[newGraph][distThreshold]["graph"])
            for (let i = 0; i < copyGraph["edges"].length; i++){
                let shouldBeHide = copyGraph["edges"][i]["value"] < similarityThreshold
                copyGraph["edges"][i]["hidden"] = shouldBeHide
            }
            setGraph(copyGraph)
            setOptions(data[newGraph][distThreshold]["options"])
            setNoMatchFound(false)
        }
        else {
            setGraph({})
            setOptions({})
            setNoMatchFound(true)
        }
    }


    return (
    <div className="main-descriptor">
        <div className="descriptor-title">
            <span style={{textAlign: 'center'}}>
                <b>Base:</b><br/> {base1}:{base2}
            </span>
            <span style={{textAlign: 'center'}}>
                <b>Target:</b><br/> {target1}:{target2}
            </span>
        </div>
        <table className="descriptor-table">
            <tbody>
                <tr>
                    <td className="descriptor-td-title" style={{width: "30%"}}>Mapping</td>
                    <td className="descriptor-td-title">Score</td>
                    <td className="descriptor-td-title">Taken from</td>
                </tr>
                <tr>
                    <td className="descriptor-td">
                        {base1}&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;{target1}
                        <br/>
                        {base2}&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;{target2}
                    </td>
                    <td className="descriptor-td">
                        {Math.round((scores[0] + scores[1]) * 1000) / 1000}
                    </td>
                    <td className="descriptor-td">
                        <button className="graph-button" onClick={() => onGraphClick(0, base1, base2, target1, target2)}>
                            <font color="red">{base1}&nbsp;.*&nbsp;{base2}</font>,&nbsp;&nbsp; 
                            <font color="#11b31e">{target1}&nbsp;.*&nbsp;{target2}</font>,&nbsp;&nbsp; 
                            {Math.round((scores[0]) * 1000) / 1000}
                        </button>
                        <button className="graph-button" onClick={() => onGraphClick(1, base2, base1, target2, target1)}>
                            <font color="red">{base2}&nbsp;.*&nbsp;{base1}</font>,&nbsp;&nbsp; 
                            <font color="#11b31e">{target2}&nbsp;.*&nbsp;{target1}</font>,&nbsp;&nbsp; 
                            {Math.round((scores[1]) * 1000) / 1000}
                        </button>
                    </td>
                </tr>
                <tr>
                    <td className="descriptor-td">
                        {base1}&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;{target2}
                        <br/>
                        {base2}&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;{target1}
                    </td>
                    <td className="descriptor-td">
                        {Math.round((scores[2] + scores[3]) * 1000) / 1000}
                    </td>
                    <td className="descriptor-td">
                        <button className="graph-button" onClick={() => onGraphClick(2, base1, base2, target2, target1)}>
                            <font color="red">{base1}&nbsp;.*&nbsp;{base2}</font>,&nbsp;&nbsp; 
                            <font color="#11b31e">{target2}&nbsp;.*&nbsp;{target1}</font>,&nbsp;&nbsp;
                            {Math.round((scores[2]) * 1000) / 1000}
                        </button>
                        <button className="graph-button" onClick={() => onGraphClick(3, base2, base1, target1, target2)}>
                            <font color="red">{base2}&nbsp;.*&nbsp;{base1}</font>,&nbsp;&nbsp; 
                            <font color="#11b31e">{target1}&nbsp;.*&nbsp;{target2}</font>,&nbsp;&nbsp; 
                            {Math.round((scores[3]) * 1000) / 1000}
                        </button>
                    </td>
                </tr>
            </tbody>
        </table>
        <div className="score-title">
            {
                noMatchFound
                ? <span>No Match found</span>
                : <></>
            }
        </div>
    </div>
    );
}

export default Descriptor;
