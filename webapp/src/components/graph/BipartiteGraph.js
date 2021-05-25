import React, {useState, useEffect} from 'react';
import { useLocation } from 'react-router-dom'
import Graph from "react-vis-network-graph";
import './BipartiteGraph.css'
import RightArrow from '../../assets/arrow-right.svg'

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

    for (let i = 0; i < data["edges"].length; i++){
      console.log(data["edges"][i]["value"])
      if (data["edges"][i]["value"] < 0.7){
        data["edges"][i]["hidden"] = true
      }
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

  // const events = {
  //   select: function(event) {
  //     var { nodes, edges } = event;
  //     console.log(edges)
  //   }
  // };

  return (
    <div>
      {graph
      ? 
        <div className="graph-container">
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
          <Graph
            graph={graph}
            options={options}
            // events={events}
          />
        </div>
      :
        <></>
      }
    </div>
  );
}

export default BipartiteGraph;
