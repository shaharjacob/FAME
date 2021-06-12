import cloneDeep from 'lodash/cloneDeep'
import React, {useState, useEffect} from 'react'

import Graph from "react-vis-network-graph"
import Slider from '@material-ui/core/Slider'
import { useLocation } from 'react-router-dom'
import LoadingOverlay from 'react-loading-overlay'
import ClipLoader from 'react-spinners/ClipLoader'

import './Graph.css'
import { IsEmpty } from '../../utils'
import RightArrow from '../../assets/arrow-right.svg'


const FullGraph = () => {

    let location = useLocation()

    const [data, setData] = useState({})
    const [graph, setGraph] = useState({})
    const [edge, setEdge] = useState(0)
    const [options, setOptions] = useState({})
    const [scores, setScores] = useState([0, 0, 0, 0])
    const [distThreshold, setDistThreshold] = useState(0.8)
    const [head1, setHead1] = useState("")
    const [tail1, setTail1] = useState("")
    const [head2, setHead2] = useState("")
    const [tail2, setTail2] = useState("")
    const [similarityThreshold, setSimilarityThreshold] = useState(0.00)
    const [alpha, setAlpha] = useState(0.0)
    const [isLoading, setIsLoading] = useState(true)
    const [noMatchFound, setNoMatchFound] = useState(false)
    // const [equation, setEquation] = useState("")
    // const [score, setScroe] = useState(0)
    // const [edgesScore, setEdgesScore] = useState([])

    // const Parser = require('expr-eval').Parser;
    // const parser = new Parser();

    useEffect(() => {
        let params = new URLSearchParams(location.search)
        setHead1(params.get('head1'))
        setHead2(params.get('head2'))
        setTail1(params.get('tail1'))
        setTail2(params.get('tail2'))
    
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
                // setEdgesScore(data[0.8]["edges_score"])
                // setEquation(data[0.8]["edges_equation"])

                // let expr = parser.parse(data[0.8]["edges_equation"]);
                // let variables = {}
                // for (let i = 0; i < data[0.8]["edges_score"].length; i++) {
                //     variables[`edge${i}`] = data[0.8]["edges_score"][i]
                // }
                // setScroe(expr.evaluate( variables ))
            }
            else {
                setNoMatchFound(true)
            }
            setIsLoading(false)
        })
      },[location])

    // const onEquationChange = (event) => {
    //     setEquation(event.target.value)
    // }

    // const onEquationSubmit = () => {
    //     let expr = parser.parse(equation);
    //     let variables = {}
    //     for (let i = 0; i < edgesScore.length; i++) {
    //         variables[`edge${i}`] = edgesScore[i]
    //     }
    //     setScroe(expr.evaluate( variables ))
    // }
    
    const onEdgeClick = (newEdge) => {
        setEdge(newEdge)
        if (!IsEmpty(data[newEdge][distThreshold]["graph"])) {
            let copyGraph = cloneDeep(data[newEdge][distThreshold]["graph"])
            for (let i = 0; i < copyGraph["edges"].length; i++){
                let shouldBeHide = copyGraph["edges"][i]["value"] < similarityThreshold
                copyGraph["edges"][i]["hidden"] = shouldBeHide
            }
            setGraph(copyGraph)
            setOptions(data[newEdge][distThreshold]["options"])
            setNoMatchFound(false)
        }
        else {
            setGraph({})
            setOptions({})
            setNoMatchFound(true)
        }
    }

    function valueTextSlider(value) {
        return `${value}`;
    }
    
    function onChangedDistThreshold(event, value) {
        let copyGraph = cloneDeep(data[edge][value]["graph"])
        for (let i = 0; i < copyGraph["edges"].length; i++){
          let shouldBeHide = copyGraph["edges"][i]["value"] < similarityThreshold
          copyGraph["edges"][i]["hidden"] = shouldBeHide
        }
        setDistThreshold(value)
        setGraph(copyGraph)
        setOptions(data[edge][value]["options"])
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

    function onChangedAlpha(event, value) {
        setAlpha(value)
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
                            <td className="td-left-edge">
                                <span className="edge-title left-edge">
                                    {head1}&nbsp;&nbsp;
                                    <img src={RightArrow} width={10} alt="-->"/>
                                    &nbsp;&nbsp;{tail1}
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
                            <td className="td-right-edge">
                                <span className="edge-title right-edge">
                                    {head2}&nbsp;&nbsp;
                                    <img src={RightArrow} width={10} alt="-->"/>
                                    &nbsp;&nbsp;{tail2}
                                </span>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>
            <div className="calculator">
                <div className="slider-calculator">
                    <Slider
                        defaultValue={alpha}
                        getAriaValueText={valueTextSlider}
                        aria-labelledby="discrete-slider-small-steps"
                        step={0.1}
                        min={0.0}
                        max={1.0}
                        valueLabelDisplay="on"
                        onChange={onChangedAlpha}
                    />
                    <span className="slider-title">
                        Weight of the opposite direction
                    </span>
                </div>
                <button className="edge-button" onClick={() => onEdgeClick(0)}>
                    <div className="score-title">
                        <font color="red">
                            {head1}&nbsp;&nbsp;
                            <img src={RightArrow} width={10} alt="-->"/>
                            &nbsp;&nbsp;{tail1}
                        </font>
                        &nbsp;~&nbsp;
                        <font color="#11b31e">
                            {head2}&nbsp;&nbsp;
                            <img src={RightArrow} width={10} alt="-->"/>
                            &nbsp;&nbsp;{tail2}
                        </font>
                        : <b>{scores[0] + scores[1] * alpha}</b>
                    </div>
                </button>
                <button className="edge-button" onClick={() => onEdgeClick(1)}>
                    <div className="score-title">
                        <font color="red">
                            {tail1}&nbsp;&nbsp;
                            <img src={RightArrow} width={10} alt="-->"/>
                            &nbsp;&nbsp;{head1}
                        </font>
                        &nbsp;~&nbsp;
                        <font color="#11b31e">
                            {tail2}&nbsp;&nbsp;
                            <img src={RightArrow} width={10} alt="-->"/>
                            &nbsp;&nbsp;{head2}
                        </font>
                        : <b>{scores[1] + scores[0] * alpha}</b>
                    </div>
                </button>
                <button className="edge-button" onClick={() => onEdgeClick(2)}>
                    <div className="score-title">
                        <font color="red">
                            {head1}&nbsp;&nbsp;
                            <img src={RightArrow} width={10} alt="-->"/>
                            &nbsp;&nbsp;{tail1}
                        </font>
                        &nbsp;~&nbsp;
                        <font color="#11b31e">
                            {tail2}&nbsp;&nbsp;
                            <img src={RightArrow} width={10} alt="-->"/>
                            &nbsp;&nbsp;{head2}
                        </font>
                        : <b>{scores[2] + scores[3] * alpha}</b>
                    </div>
                </button>
                <button className="edge-button" onClick={() => onEdgeClick(3)}>
                    <div className="score-title">
                        <font color="red">
                            {tail1}&nbsp;&nbsp;
                            <img src={RightArrow} width={10} alt="-->"/>
                            &nbsp;&nbsp;{head1}
                        </font>
                        &nbsp;~&nbsp;
                        <font color="#11b31e">
                            {head2}&nbsp;&nbsp;
                            <img src={RightArrow} width={10} alt="-->"/>
                            &nbsp;&nbsp;{tail2}
                        </font>
                        : <b>{scores[3] + scores[2] * alpha}</b>
                    </div>
                </button>
                <div className="score-title">
                    {
                        noMatchFound
                        ? <span>No Match found</span>
                        : <></>
                    }
                </div>
                {/* <div className="equation-title">
                    Equation:
                </div>
                <div>
                    <textarea className="equation" type="text" value={equation} onChange={onEquationChange} />
                </div>
                <div className="button-equation">
                    <button className="btn btn-primary" onClick={onEquationSubmit}>Submit</button>
                </div>
                <div className="score-title">
                    Score:
                </div>
                <div className="score">
                    {score}
                </div> */}
            </div>
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
