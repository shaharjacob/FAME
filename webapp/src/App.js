import React, {useState, useEffect} from 'react';
import Graph from "react-vis-network-graph";

const App = () => {

  const [graph, setGraph] = useState({})

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async() => {
    const response = await fetch('/api')
    const data = await response.json()
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

export default App;
