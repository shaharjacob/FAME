import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom'
import BipartiteGraph from './components/graph/BipartiteGraph'
import Cluster from './components/graph/Cluster'
import TwoEntities from './components/graph/TwoEntities'
import Mapping from './components/graph/Mapping'
import TestViewer from './components/graph/TestViewer'
import Main from './components/main/Main'
import MappingDemo from './components/main/MappingDemo'


const App = () => {

  return (
    <Router>
      <div>
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
          <Route path='/two-entities'>
            <TwoEntities />
          </Route>
          <Route path='/mapping'>
            <Mapping />
          </Route>
          <Route path='/mapping-demo'>
            <MappingDemo />
          </Route>
          <Route path='/relations-demo'>
            <Main />
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
