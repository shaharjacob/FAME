import React, {useState, useEffect} from 'react'

import Select from 'react-select';
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
    const [data, setData] = useState([])
    const [topSuggestions, setTopSuggestions] = useState([])

    // general
    const [isLoading, setIsLoading] = useState(true)
    const [baseEntities, setBaseEntities] = useState([])
    const [targetEntities, setTargetEntities] = useState([])
    const [exeutionTime, setExeutionTime] = useState(0)
    const [topSolutionsOptions, setTopSolutionsOptions] = useState([])

    useEffect(() => {
        let params = new URLSearchParams(location.search)
        setBaseEntities(params.get("base"))
        setTargetEntities(params.get("target"))

        let prefix = ""
        if (process.env.NODE_ENV === "production") {
            prefix = "http://localhost:5031"
        }
        fetch(`${prefix}/api/mapping?` + params).then(response => {
          if(response.ok){
            return response.json()
          }
        }).then(data => {
            if (!IsEmpty(data) && data["data"].length > 0 && !IsEmpty(data["data"][0]["graph"])) {
                setData(data["data"])
                setGraph(data["data"][0]["graph"])
                setTopSuggestions(data["data"][0]["top_suggestions"])
                setTopSolutionsOptions(data["scores"])
                setExeutionTime(data["time"])
                setIsLoading(false)
            }
        })
      },[location.search])

    function onChangeTopSolutions(obj) {
        setGraph(data[obj.value]["graph"])
        setTopSuggestions(data[obj.value]["top_suggestions"])
    }

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
                    <div>
                        <div>
                            <i className="fas fa-trophy gold"></i>&nbsp;<span className="mapping-titles">Top solutions</span>
                            <Select
                                className="select-top-solutions"
                                onChange={(obj) => onChangeTopSolutions(obj)}
                                options={topSolutionsOptions}
                            />
                        </div>
                    </div>
                    {topSuggestions.length > 0
                    ?
                        <div>
                            <div><i className="far fa-lightbulb gold"></i>&nbsp;<span className="mapping-titles">Suggestions</span></div>
                            <div><code>{topSuggestions.join(",")}</code></div>
                        </div>
                    :
                        <div></div>
                    }
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
