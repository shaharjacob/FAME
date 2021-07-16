import React, {useState, useEffect} from 'react'

import Graph from "react-vis-network-graph"
import { useLocation } from 'react-router-dom'
import LoadingOverlay from 'react-loading-overlay'
import ClipLoader from 'react-spinners/ClipLoader'

import './Graph.css'
import './Mapping.css'
import { IsEmpty } from '../../utils'


const Mapping = () => {

    let location = useLocation()

    // graph viewer
    const [graph, setGraph] = useState({})

    // general
    const [isLoading, setIsLoading] = useState(true)
    const [baseEntities, setBaseEntities] = useState([])
    const [targetEntities, setTargetEntities] = useState([])
    const [exeutionTime, setExeutionTime] = useState(0)

    useEffect(() => {
        let params = new URLSearchParams(location.search)
        setBaseEntities(params.get("base"))
        setTargetEntities(params.get("target"))

        fetch('/mapping?' + params).then(response => {
          if(response.ok){
            return response.json()
          }
        }).then(data => {
            if (!IsEmpty(data) && !IsEmpty(data["graph"])) {
                setGraph(data["graph"])
                setExeutionTime(data["time"])
                setIsLoading(false)
            }
        })
      },[location.search])

    const options = {
        height: "800px",
        physics: {
            enabled: false
        }
      };

    function getNodeLabelByID(id) {
        for (let i = 0; i < graph.nodes.length; i++) {
            if (graph.nodes[i].id === id) {
                return graph.nodes[i].label
            }
        }
    }
    
    const events = {
        select: function(event) {
            var { nodes, edges } = event;
            if (edges.length === 1) {
                var edge = edges[0].split(":")
                var map1 = getNodeLabelByID(parseInt(edge[0])).split(" --> ")
                var map2 = getNodeLabelByID(parseInt(edge[1])).split(" --> ")
                window.open(`/single-mapping?base1=${map1[0]}&base2=${map2[0]}&target1=${map1[1]}&target2=${map2[1]}`, '_blank').focus();
            }
        }
    };


    return (
    <div>
        {!isLoading && graph
        ?
            <div className="mapping-container">
                <div className="mapping-top">
                    <div></div>
                    <div>
                        <div><i className="fas fa-home text-blue"></i>&nbsp;<span className="mapping-titles">Base</span></div>
                        <div><code>{baseEntities}</code></div>
                    </div>
                    <div>
                        <div><i className="fas fa-dot-circle text-red"></i>&nbsp;<span className="mapping-titles">Target</span></div>
                        <div><code>{targetEntities}</code></div>
                    </div>
                    <div>
                        <div><i className="far fa-clock dark-gray"></i>&nbsp;<span className="mapping-titles">Execution time</span></div>
                        <div><code>{exeutionTime} sec</code></div>
                    </div>
                    <div></div>
                </div>
                <Graph
                    graph={graph}
                    options={options}
                    events={events}
                />
            </div>
        :
            <div className="overlay-loading">
                <LoadingOverlay
                    active={isLoading}
                    spinner={<ClipLoader size={70} color="#469cac" />}
                />
            </div>
        }
    </div>
    );
}

export default Mapping;
