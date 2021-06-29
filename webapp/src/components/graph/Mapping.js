import React, {useState, useEffect} from 'react'

import Graph from "react-vis-network-graph"
import { useLocation } from 'react-router-dom'

import './Graph.css'
import { IsEmpty } from '../../utils'


const Mapping = () => {

    let location = useLocation()

    // graph viewer
    const [graph, setGraph] = useState({})

    useEffect(() => {
        let params = new URLSearchParams(location.search)
    
        fetch('/mapping?' + params).then(response => {
          if(response.ok){
            return response.json()
          }
        }).then(data => {
            if (!IsEmpty(data) && !IsEmpty(data["graph"])) {
                setGraph(data["graph"])
            }
        })
      },[location])

    const options = {
        height: "800px",
        physics: {
            enabled: false
        }
      };
    
    const events = {
        select: function(event) {
            var { nodes, edges } = event;
            console.log(nodes)
            console.log(edges)
        }
    };


    return (
    <div>
        {graph
        ?
            <Graph
                graph={graph}
                options={options}
            />
        :
            <></>
        }
    </div>
    );
}

export default Mapping;
