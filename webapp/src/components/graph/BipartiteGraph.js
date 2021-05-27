import React, {useState, useEffect} from 'react';
import { useLocation } from 'react-router-dom'
import Graph from "react-vis-network-graph";
import './Graph.css'
import RightArrow from '../../assets/arrow-right.svg'
import Slider from '@material-ui/core/Slider';
import cloneDeep from 'lodash/cloneDeep';

const BipartiteGraph = () => {

  let location = useLocation()

  const [graph, setGraph] = useState({})
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
    const response = await fetch('/api?' + params)
    const data = await response.json()
    setGraph(data)
  }

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

export default BipartiteGraph;
