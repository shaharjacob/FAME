import React from 'react';
import { BrowserRouter as Router, Route, Switch } from 'react-router-dom'
import BipartiteGraph from './components/graph/BipartiteGraph'
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
        </Switch>
      </div>
    </Router>
  );
}

export default App;
