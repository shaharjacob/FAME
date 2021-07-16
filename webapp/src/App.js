import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom'

// graph
import Mapping from './components/graph/Mapping'
import Cluster from './components/graph/Cluster'
import TestViewer from './components/graph/TestViewer'
import SingleMapping from './components/graph/SingleMapping'
import BipartiteGraph from './components/graph/BipartiteGraph'

// demo 
import MappingDemo from './components/demo/MappingDemo'
import TwoEntitiesDemo from './components/demo/TwoEntitiesDemo'
import SingleMappingDemo from './components/demo/SingleMappingDemo'

// others
import Main from './components/main/Main'
import Navbar from './components/navbar/Navbar'
import TwoEntities from './components/entities/TwoEntities'


const App = () => {

  return (
    <Router>
      <div>
        <Navbar />
        <Switch>
          <Route path='/' exact>
            <Main />
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
          <Route path='/two-entities-demo'>
            <TwoEntitiesDemo />
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
