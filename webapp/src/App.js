import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom'
import BipartiteGraph from './components/graph/BipartiteGraph'
import Cluster from './components/graph/Cluster'
import FullGraph from './components/graph/FullGraph'
import Test from './components/graph/Test'
import Main from './components/main/Main'


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
          <Route path='/graph'>
            <FullGraph />
          </Route>
          <Route path='/test'>
            <Test />
          </Route>
        </Switch>
      </div>
    </Router>
  );
}

export default App;
