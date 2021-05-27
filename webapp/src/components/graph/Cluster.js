import React, {useState, useEffect} from 'react';
import { useLocation } from 'react-router-dom'
import Graph from "react-vis-network-graph";
import RightArrow from '../../assets/arrow-right.svg'
import Slider from '@material-ui/core/Slider';
import './Graph.css'


const Cluster = () => {

    let location = useLocation()

    const [data, setData] = useState({})
    const [graph, setGraph] = useState({})
    const [options, setOptions] = useState({})
    const [head1, setHead1] = useState("")
    const [tail1, setTail1] = useState("")
    const [head2, setHead2] = useState("")
    const [tail2, setTail2] = useState("")

    useEffect(() => {
        loadData()
    }, [])

    const loadData = async() => {
        let params = new URLSearchParams(location.search)
        setHead1(params.get('head1'))
        setHead2(params.get('head2'))
        setTail1(params.get('tail1'))
        setTail2(params.get('tail2'))
        const response = await fetch('/cluster?' + params)
        const data = await response.json()
        setData(data)
        setGraph(data[0.8]["graph"])
        setOptions(data[0.8]["options"])
    }

    function valuetext(value) {
        return `${value}`;
    }
    
    function onThresholdChanged(event, value) {
        setGraph(data[value]["graph"])
        setOptions(data[value]["options"])
    }

    return (
    <div>
        {graph && options
        ? 
        <div className="graph-container">
            <div className="graph-top">
                <div className="graph-title">
                    <span className="left-edge">
                        {head1}&nbsp;&nbsp;
                        <img src={RightArrow} width={10} alt="-->"/>
                        &nbsp;&nbsp;{tail1}
                    </span>
                    ~
                    <span className="right-edge">
                        {head2}&nbsp;&nbsp;
                        <img src={RightArrow} width={10} alt="-->"/>
                        &nbsp;&nbsp;{tail2}
                    </span>
                </div>
                <div className="slider">
                    <Slider
                        defaultValue={0.8}
                        getAriaValueText={valuetext}
                        aria-labelledby="discrete-slider-small-steps"
                        step={0.1}
                        min={0.1}
                        max={0.9}
                        valueLabelDisplay="on"
                        onChange={onThresholdChanged}
                    />
                    <span className="slider-title">
                        Distance Threshold (Clustering)
                    </span>
                </div>
            </div>
            <Graph
                graph={graph}
                options={options}
            />
        </div>
        :
        <></>
        }
    </div>
    );
}

export default Cluster;
