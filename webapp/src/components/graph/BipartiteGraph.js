import cloneDeep from 'lodash/cloneDeep';
import React, {useState, useEffect} from 'react';

import Graph from "react-vis-network-graph";
import { useLocation } from 'react-router-dom'
import Slider from '@material-ui/core/Slider';
import LoadingOverlay from 'react-loading-overlay'
import ClipLoader from 'react-spinners/ClipLoader'

import './Graph.css'
import { IsEmpty } from '../../utils'
import RightArrow from '../../assets/arrow-right.svg'


const BipartiteGraph = () => {

  let location = useLocation()

  const [graph, setGraph] = useState({})
  const [head1, setHead1] = useState("")
  const [tail1, setTail1] = useState("")
  const [head2, setHead2] = useState("")
  const [tail2, setTail2] = useState("")
  const [isLoading, setIsLoading] = useState(true)
  const [noMatchFound, setNoMatchFound] = useState(false)

  useEffect(() => {
    let params = new URLSearchParams(location.search)
    setHead1(params.get('head1'))
    setHead2(params.get('head2'))
    setTail1(params.get('tail1'))
    setTail2(params.get('tail2'))

    fetch('/bipartite?' + params).then(response => {
      if(response.ok){
        return response.json()
      }
    }).then(data => {
        if (IsEmpty(data)) {
          setGraph(data)
        }
        else {
          setNoMatchFound(true)
        }
        setIsLoading(false)
    })
  },[])

  function valuetext(value) {
    return `${value}`;
  }

  function onThresholdChanged(event, value) {
    let data = cloneDeep(graph)
    for (let i = 0; i < data["edges"].length; i++){
      let shouldBeHide = data["edges"][i]["value"] < value
      data["edges"][i]["hidden"] = shouldBeHide
    }
    setGraph(data)
  }

  const options = {
    physics: {
      enabled: false,
    },
    height: "800px",
    groups: {
      0: {color:{background:'orange'}, borderWidth:1},
      1: {color:{background:'cyan'}, borderWidth:1}
    }
  };

  return (
    <div>
      {graph
      ? 
        <div className="graph-container">
          <div className="graph-top">
            <div className="graph-title">
              <span className="edge-title left-edge">
                {head1}&nbsp;&nbsp;
                <img src={RightArrow} width={10} alt="-->"/>
                &nbsp;&nbsp;{tail1}
              </span>
              &nbsp;&nbsp; &nbsp;&nbsp;~ &nbsp;&nbsp; &nbsp;&nbsp;
              <span className="edge-title right-edge">
                {head2}&nbsp;&nbsp;
                <img src={RightArrow} width={10} alt="-->"/>
                &nbsp;&nbsp;{tail2}
              </span>
            </div>
            <div className="slider">
              <Slider
                defaultValue={0.00}
                getAriaValueText={valuetext}
                aria-labelledby="discrete-slider-small-steps"
                step={0.01}
                min={0.00}
                max={1.00}
                valueLabelDisplay="on"
                onChange={onThresholdChanged}
              />
              <span className="slider-title">
                  Similarity Threshold (Clustering)
              </span>
            </div>
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

export default BipartiteGraph;
