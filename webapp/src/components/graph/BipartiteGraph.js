import cloneDeep from 'lodash/cloneDeep';
import React, {useState, useEffect} from 'react';

import Graph from "react-vis-network-graph";
import { useLocation } from 'react-router-dom'
import Slider from '@material-ui/core/Slider';
import LoadingOverlay from 'react-loading-overlay'
import ClipLoader from 'react-spinners/ClipLoader'

import './Graph.css'
import './GraphWithoutDescriptor.css'
import { IsEmpty } from '../../utils'


const BipartiteGraph = () => {

  let location = useLocation()

  const [graph, setGraph] = useState({})
  const [base1, setBase1] = useState("")
  const [base2, setBase2] = useState("")
  const [target1, setTarget1] = useState("")
  const [target2, setTarget2] = useState("")
  const [isLoading, setIsLoading] = useState(true)
  const [noMatchFound, setNoMatchFound] = useState(false)

  useEffect(() => {
    let params = new URLSearchParams(location.search)
    setBase1(params.get('base1'))
    setTarget1(params.get('target1'))
    setBase2(params.get('base2'))
    setTarget2(params.get('target2'))

    let prefix = ""
    if (process.env.NODE_ENV === "production") {
        prefix = "http://localhost:5031"
    }
    fetch(`${prefix}/api/bipartite?` + params)
    .then(response => {
      if(response.ok){
        return response.json()
      }
    }).then(data => {
        if (!IsEmpty(data)) {
          setGraph(data)
        }
        else {
          setNoMatchFound(true)
        }
        setIsLoading(false)
    })
  },[location])

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
        <div className="bipartie-container">
          <div className="graph-top">
            <div className="graph-title">
              <span className="entities-title base">
                {base1}&nbsp;.*&nbsp;{base2}
              </span>
              &nbsp;&nbsp; &nbsp;&nbsp;~ &nbsp;&nbsp; &nbsp;&nbsp;
              <span className="entities-title target">
                {target1}&nbsp;.*&nbsp;{target2}
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
