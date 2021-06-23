import cloneDeep from 'lodash/cloneDeep'
import React from 'react'

import './Graph.css'
import { IsEmpty } from '../../utils'
import RightArrow from '../../assets/arrow-right.svg'

const Descriptor = ({data, setGraph, setGraphSelect, setOptions, scores, distThreshold, B, setCurrB, T, setCurrT, similarityThreshold, noMatchFound, setNoMatchFound}) => {

    const onGraphClick = (newGraph, entity1, entity2, entity3, entity4) => {
        setCurrB([entity1, entity2])
        setCurrT([entity3, entity4])
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
                <b>Base:</b><br/> {B.join(':')}
            </span>
            <span style={{textAlign: 'center'}}>
                <b>Target:</b><br/> {T.join(':')}
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
                        {B[0]}&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;{T[0]}
                        <br/>
                        {B[1]}&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;{T[1]}
                    </td>
                    <td className="descriptor-td">
                        {Math.round((scores[0] + scores[1]) * 1000) / 1000}
                    </td>
                    <td className="descriptor-td">
                        <button className="graph-button" onClick={() => onGraphClick(0, B[0], B[1], T[0], T[1])}>
                            <font color="red">{B[0]}&nbsp;.*&nbsp;{B[1]}</font>,&nbsp;&nbsp; 
                            <font color="#11b31e">{T[0]}&nbsp;.*&nbsp;{T[1]}</font>,&nbsp;&nbsp; 
                            {Math.round((scores[0]) * 1000) / 1000}
                        </button>
                        <button className="graph-button" onClick={() => onGraphClick(1, B[1], B[0], T[1], T[0])}>
                            <font color="red">{B[1]}&nbsp;.*&nbsp;{B[0]}</font>,&nbsp;&nbsp; 
                            <font color="#11b31e">{T[1]}&nbsp;.*&nbsp;{T[0]}</font>,&nbsp;&nbsp; 
                            {Math.round((scores[1]) * 1000) / 1000}
                        </button>
                    </td>
                </tr>
                <tr>
                    <td className="descriptor-td">
                        {B[0]}&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;{T[1]}
                        <br/>
                        {B[1]}&nbsp;<img src={RightArrow} width={10} alt="-->"/>&nbsp;{T[0]}
                    </td>
                    <td className="descriptor-td">
                        {Math.round((scores[2] + scores[3]) * 1000) / 1000}
                    </td>
                    <td className="descriptor-td">
                        <button className="graph-button" onClick={() => onGraphClick(2, B[0], B[1], T[1], T[0])}>
                            <font color="red">{B[0]}&nbsp;.*&nbsp;{B[1]}</font>,&nbsp;&nbsp; 
                            <font color="#11b31e">{T[1]}&nbsp;.*&nbsp;{T[0]}</font>,&nbsp;&nbsp;
                            {Math.round((scores[2]) * 1000) / 1000}
                        </button>
                        <button className="graph-button" onClick={() => onGraphClick(3, B[1], B[0], T[0], T[1])}>
                            <font color="red">{B[1]}&nbsp;.*&nbsp;{B[0]}</font>,&nbsp;&nbsp; 
                            <font color="#11b31e">{T[0]}&nbsp;.*&nbsp;{T[1]}</font>,&nbsp;&nbsp; 
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
