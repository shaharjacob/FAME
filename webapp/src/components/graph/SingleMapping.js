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


const SingleMapping = () => {

    let location = useLocation()
    const default_dist_th = 0.5

    // graph viewer
    const [data, setData] = useState({})
    const [graph, setGraph] = useState({})
    const [options, setOptions] = useState({})
    const [graphSelect, setGraphSelect] = useState(0)
    const [distThreshold, setDistThreshold] = useState(default_dist_th)
    const [similarityThreshold, setSimilarityThreshold] = useState(0.00)
    const [currB, setCurrB] = useState([])
    const [currT, setCurrT] = useState([])
    
    // descriptor
    const [B, setB] = useState([])
    const [T, setT] = useState([])
    const [scores, setScores] = useState([0, 0, 0, 0])
    
    // general
    const [isLoading, setIsLoading] = useState(true)
    const [noMatchFound, setNoMatchFound] = useState(false)

    useEffect(() => {
        let params = new URLSearchParams(location.search)
        
        let base = []
        let target = []
        for (const [key, value] of params.entries()) {
            if (key.includes("base")) {
                base.push(value)
            }
            if (key.includes("target")) {
                target.push(value)
            } 
        }
        
        // entities for the descriptor
        setB(base)
        setT(target)
        
        // entities which currently display
        setCurrB(base)
        setCurrT(target)
        
        let prefix = ""
        if (process.env.NODE_ENV === "production") {
            prefix = "http://localhost:5031"
        }
        fetch(`${prefix}/api/single-mapping?` + params).then(response => {
          if(response.ok){
            return response.json()
          }
        }).then(data => {
            let idx = 0
            let length = Object.keys(data).length
            for (let i = 0; i < length; i++) {
                if (!IsEmpty(data[i][default_dist_th]["graph"])) {
                    idx = i
                    break
                }
            }
            if (!IsEmpty(data[idx][default_dist_th]["graph"])) {
                setData(data)
                setGraph(data[idx][default_dist_th]["graph"])
                setOptions(data[idx][default_dist_th]["options"])
                setScores([
                    data[0][default_dist_th]["score"],
                    data[1][default_dist_th]["score"],
                    data[2][default_dist_th]["score"],
                    data[3][default_dist_th]["score"]
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

    const events = {
        select: function(event) {
            var { nodes, edges } = event;
            if (edges.length === 1) {
                let edge_id = edges[0]
                let nodes_ids = edge_id.split(":")
                let labels1 = []
                let labels2 = []
                for (let i = 0; i < graph.nodes.length; i++){
                    if (parseInt(graph.nodes[i].id) === parseInt(nodes_ids[0])){
                        labels1 = graph.nodes[i].label.split("\n")
                    }
                    if (parseInt(graph.nodes[i].id) === parseInt(nodes_ids[1])){
                        labels2 = graph.nodes[i].label.split("\n")
                    }
                }
                window.open(`/bipartite?left=${labels1}&right=${labels2}`, '_blank').focus();
            }
        }
    };

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
                                    {currB[0]}&nbsp;.*&nbsp;{currB[1]}
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
                                    {currT[0]}&nbsp;.*&nbsp;{currT[1]}
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
                B={B}
                setCurrB={setCurrB}
                T={T}
                setCurrT={setCurrT}
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
                    events={events}
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

export default SingleMapping;
