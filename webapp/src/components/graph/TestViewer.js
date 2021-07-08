import React from 'react'
import Graph from "react-vis-network-graph"
import './Graph.css'


const TestViewer = () => {

    function get_nodes() {
        let labels = ["earth --> electrons", "sun --> nucleus", "gravity --> electricity", "newton --> faraday"]
        let nodes = []
        for (let i = 0; i < labels.length; i++) {
            nodes.push({
                id: i, 
                x: i * 250,
                label: labels[i], 
                font: "12px arial #343434"
            })
        }
        return nodes
    }

    function get_edges() {
        let edges = []
        let edge1 = {
            id: "0to1",
            from: 0, 
            to: 1, 
            scaling: {
                min: 0.01,
                max: 1,
                label: {
                    enabled: true,
                    min: 6,
                    max: 10,
                },
            },
            font: {
                align: 'left',
            },
            label: "base first line::target first line\nbase second line::target second line",
            value: 1,
            width: 0.5,
            smooth: {
                enabled: true,
                type: "curvedCW",
                roundness: 0.3,
            },
            arrows: {
                from: { enabled: false },
                to: { enabled: true },
            },
        }
        let edge2 = {
            id: "1to0",
            from: 1, 
            to: 0, 
            scaling: {
                min: 0.01,
                max: 1,
                label: {
                    enabled: true,
                    min: 4,
                    max: 8,
                },
            },
            font: {
                align: 'left',
            },
            label: "right to left",
            value: 0.9,
            width: 0.5,
            smooth: {
                enabled: true,
                type: "curvedCW",
                roundness: 0.3,
            },
            arrows: {
                from: { enabled: false },
                to: { enabled: true },
            },
        }
        let edge3 = {
            id: "2to3",
            from: 2, 
            to: 3, 
            scaling: {
                min: 0.01,
                max: 1,
                label: {
                    enabled: true,
                    min: 6,
                    max: 10,
                },
            },
            font: {
                align: 'left',
            },
            label: "base first line::target first line\nbase second line::target second line",
            value: 0.6,
            width: 0.5,
            smooth: {
                enabled: true,
                type: "curvedCW",
                roundness: 0.3,
            },
            arrows: {
                from: { enabled: false },
                to: { enabled: true },
            },
        }
        let edge4 = {
            id: "3to2",
            from: 3, 
            to: 2, 
            scaling: {
                min: 0.01,
                max: 1,
                label: {
                    enabled: true,
                    min: 8,
                    max: 12,
                },
            },
            font: {
                align: 'left',
            },
            label: "right to left",
            value: 1,
            width: 0.5,
            smooth: {
                enabled: true,
                type: "curvedCW",
                roundness: 0.3,
            },
            arrows: {
                from: { enabled: false },
                to: { enabled: true },
            },
        }
        let edge5 = {
            id: "0to3",
            from: 0, 
            to: 3, 
            scaling: {
                min: 0.01,
                max: 1,
                label: {
                    enabled: true,
                    min: 8,
                    max: 12,
                },
            },
            font: {
                align: 'left',
            },
            label: "base first line::target first line\nbase second line::target second line",
            value: 0.6,
            width: 0.5,
            smooth: {
                enabled: true,
                type: "curvedCW",
                roundness: 0.3,
            },
            arrows: {
                from: { enabled: false },
                to: { enabled: true },
            },
        }
        let edge6 = {
            id: "3to0",
            from: 3, 
            to: 0, 
            scaling: {
                min: 0.01,
                max: 1,
                label: {
                    enabled: true,
                    min: 8,
                    max: 12,
                },
            },
            font: {
                align: 'left',
            },
            label: "right to left",
            value: 0.5,
            width: 0.5,
            smooth: {
                enabled: true,
                type: "curvedCW",
                roundness: 0.3,
            },
            arrows: {
                from: { enabled: false },
                to: { enabled: true },
            },
        }
        edges.push(edge1)
        edges.push(edge2)
        edges.push(edge3)
        edges.push(edge4)
        edges.push(edge5)
        edges.push(edge6)
        return edges
    }

    const graph = {
        nodes: get_nodes(),
        edges: get_edges()
    }

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
        <Graph
            graph={graph}
            options={options}
            events={events}
        />
    </div>
    );
}

export default TestViewer;




