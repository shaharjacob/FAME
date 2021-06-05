import cloneDeep from 'lodash/cloneDeep'
import React, {useState, useEffect} from 'react'

import Graph from "react-vis-network-graph"
import Slider from '@material-ui/core/Slider'
import { useLocation } from 'react-router-dom'
import LoadingOverlay from 'react-loading-overlay'
import ClipLoader from 'react-spinners/ClipLoader'

import './Graph.css'
import RightArrow from '../../assets/arrow-right.svg'


const Test = () => {

    let location = useLocation()

    const [data, setData] = useState({})
    const [graph, setGraph] = useState({})
    const [options, setOptions] = useState({})
    const [head1, setHead1] = useState("")
    const [tail1, setTail1] = useState("")
    const [head2, setHead2] = useState("")
    const [tail2, setTail2] = useState("")
    const [similarityThreshold, setSimilarityThreshold] = useState(0.00)
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        let params = new URLSearchParams(location.search)
        setHead1(params.get('head1'))
        setHead2(params.get('head2'))
        setTail1(params.get('tail1'))
        setTail2(params.get('tail2'))
    
        fetch('/test?' + params).then(response => {
          if(response.ok){
            return response.json()
          }
        }).then(data => {
            setData(data)
            setGraph(data[0.8]["graph"])
            setOptions(data[0.8]["options"])
            setIsLoading(false)
        })
      },[])

    function valueTextDistThreshold(value) {
        return `${value}`;
    }
    
    function onChangedDistThreshold(event, value) {
        let copyGraph = cloneDeep(data[value]["graph"])
        for (let i = 0; i < copyGraph["edges"].length; i++){
          let shouldBeHide = copyGraph["edges"][i]["value"] < similarityThreshold
          copyGraph["edges"][i]["hidden"] = shouldBeHide
        }
        setGraph(copyGraph)
        setOptions(data[value]["options"])
    }

    function valueTextSimilarityThreshold(value) {
        return `${value}`;
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
            <table>
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
                                defaultValue={0.8}
                                getAriaValueText={valueTextDistThreshold}
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
                                getAriaValueText={valueTextSimilarityThreshold}
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
            </table>
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
        </div>
        :
        <></>
        }
    </div>
    );
}

export default Test;
