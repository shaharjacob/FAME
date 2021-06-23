import cloneDeep from 'lodash/cloneDeep'
import React, {useState, useEffect} from 'react'

import Graph from "react-vis-network-graph"
import Slider from '@material-ui/core/Slider'
import { useLocation } from 'react-router-dom'
import LoadingOverlay from 'react-loading-overlay'
import ClipLoader from 'react-spinners/ClipLoader'

import './Graph.css'
import Descriptor from './Descriptor'
import { IsEmpty } from '../../utils'


const FullGraph = () => {

    let location = useLocation()

    // graph viewer
    const [data, setData] = useState({})
    const [graph, setGraph] = useState({})
    const [options, setOptions] = useState({})
    const [graphSelect, setGraphSelect] = useState(0)
    const [distThreshold, setDistThreshold] = useState(0.8)
    const [similarityThreshold, setSimilarityThreshold] = useState(0.00)
    const [currBase1, setCurrBase1] = useState("")
    const [currBase2, setCurrBase2] = useState("")
    const [currTarget1, setCurrTarget1] = useState("")
    const [currTarget2, setCurrTarget2] = useState("")
    
    // descriptor
    const [base1, setBase1] = useState("")
    const [base2, setBase2] = useState("")
    const [target1, setTarget1] = useState("")
    const [target2, setTarget2] = useState("")
    const [scores, setScores] = useState([0, 0, 0, 0])
    
    // general
    const [isLoading, setIsLoading] = useState(true)
    const [noMatchFound, setNoMatchFound] = useState(false)

    useEffect(() => {
        let params = new URLSearchParams(location.search)

        // entities for the descriptor
        setBase1(params.get('base1'))
        setBase2(params.get('base2'))
        setTarget1(params.get('target1'))
        setTarget2(params.get('target2'))

        // entities which currently display
        setCurrBase1(params.get('base1'))
        setCurrBase2(params.get('base2'))
        setCurrTarget1(params.get('target1'))
        setCurrTarget2(params.get('target2'))
    
        fetch('/full?' + params).then(response => {
          if(response.ok){
            return response.json()
          }
        }).then(data => {
            if (!IsEmpty(data[0][0.8]["graph"])) {
                setData(data)
                setGraph(data[0][0.8]["graph"])
                setOptions(data[0][0.8]["options"])
                setScores([
                    data[0][0.8]["score"],
                    data[1][0.8]["score"],
                    data[2][0.8]["score"],
                    data[3][0.8]["score"]
                ])
            }
            else {
                setNoMatchFound(true)
            }
            setIsLoading(false)
        })
      },[location])

    function valueTextSlider(value) {
        return `${value}`;
    }
    
    function onChangedDistThreshold(event, value) {
        let copyGraph = cloneDeep(data[graphSelect][value]["graph"])
        for (let i = 0; i < copyGraph["edges"].length; i++){
          let shouldBeHide = copyGraph["edges"][i]["value"] < similarityThreshold
          copyGraph["edges"][i]["hidden"] = shouldBeHide
        }
        setDistThreshold(value)
        setGraph(copyGraph)
        setOptions(data[graphSelect][value]["options"])
        setScores([
            data[0][value]["score"],
            data[1][value]["score"],
            data[2][value]["score"],
            data[3][value]["score"]
        ])
    }
    
    function onChangedSimilarityThreshold(event, value) {
        let copyGraph = cloneDeep(graph)
        for (let i = 0; i < copyGraph["edges"].length; i++){
            let shouldBeHide = copyGraph["edges"][i]["value"] < value
            copyGraph["edges"][i]["hidden"] = shouldBeHide
        }
        setGraph(copyGraph)
        setSimilarityThreshold(value)
    }

    return (
    <div>
        {graph && options
        ? 
        <div className="graph-container">
            <div className="top">
                <table>
                    <tbody>
                        <tr>
                            <td className="td-base">
                                <span className="entities-title base">
                                    {currBase1}&nbsp;.*&nbsp;{currBase2}
                                </span>
                            </td>
                            <td className="td-slider">
                                <div className="slider">
                                    <Slider
                                        defaultValue={distThreshold}
                                        getAriaValueText={valueTextSlider}
                                        aria-labelledby="discrete-slider-small-steps"
                                        step={0.1}
                                        min={0.1}
                                        max={0.9}
                                        valueLabelDisplay="on"
                                        onChange={onChangedDistThreshold}
                                    />
                                    <span className="slider-title">
                                        Distance Threshold (Clustering)
                                    </span>
                                </div>
                            </td>
                            <td className="td-slider">
                                <div className="slider">
                                    <Slider
                                        defaultValue={similarityThreshold}
                                        getAriaValueText={valueTextSlider}
                                        aria-labelledby="discrete-slider-small-steps"
                                        step={0.01}
                                        min={0.00}
                                        max={1.00}
                                        valueLabelDisplay="on"
                                        onChange={onChangedSimilarityThreshold}
                                    />
                                    <span className="slider-title">
                                        Similarity Threshold (Edges)
                                    </span>
                                </div>
                            </td>
                            <td className="td-target">
                                <span className="entities-title target">
                                    {currTarget1}&nbsp;.*&nbsp;{currTarget2}
                                </span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <Descriptor 
                data={data} 
                setGraph={setGraph} 
                setGraphSelect={setGraphSelect} 
                setOptions={setOptions} 
                scores={scores} 
                distThreshold={distThreshold} 
                base1={base1} 
                setCurrBase1={setCurrBase1}
                base2={base2} 
                setCurrBase2={setCurrBase2}
                target1={target1} 
                setCurrTarget1={setCurrTarget1}
                target2={target2}
                setCurrTarget2={setCurrTarget2}
                similarityThreshold={similarityThreshold} 
                noMatchFound={noMatchFound} 
                setNoMatchFound={setNoMatchFound}
            />
            {isLoading
            ?
                <div className="overlay-loading">
                    <LoadingOverlay
                        active={isLoading}
                        spinner={<ClipLoader size={70} color="#469cac" />}
                    />
                </div>
            :
                <Graph
                    graph={graph}
                    options={options}
                />
            }
            {
                noMatchFound
                ? <span style={{textAlign: 'center'}}>No Match found</span>
                : <></>
            }
        </div>
        :
        <></>
        }
    </div>
    );
}

export default FullGraph;
