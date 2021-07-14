import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom'
import BipartiteGraph from './components/graph/BipartiteGraph'
import Cluster from './components/graph/Cluster'
import SingleMapping from './components/graph/SingleMapping'
import TwoEntities from './components/entities/TwoEntities'
import Mapping from './components/graph/Mapping'
import TestViewer from './components/graph/TestViewer'
import SingleMappingDemo from './components/demo/SingleMappingDemo'
import MappingDemo from './components/demo/MappingDemo'


const App = () => {

  return (
    <Router>
      <div>
        <Switch>
          <Route path='/' exact>
            <MappingDemo />
          </Route>
          <Route path='/bipartite'>
            <BipartiteGraph />
          </Route>
          <Route path='/cluster'>
            <Cluster />
          </Route>
          <Route path='/single-mapping'>
            <SingleMapping />
          </Route>
          <Route path='/two-entities'>
            <TwoEntities />
          </Route>
          <Route path='/mapping'>
            <Mapping />
          </Route>
          <Route path='/mapping-demo'>
            <MappingDemo />
          </Route>
          <Route path='/single-mapping-demo'>
            <SingleMappingDemo />
          </Route>
          <Route path='/test'>
            <TestViewer />
          </Route>
        </Switch>
      </div>
    </Router>
  );
}

export default App;
