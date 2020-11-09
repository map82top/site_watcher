import ReactDOM from 'react-dom';
import React, { useEffect } from "react";
import './styles/index.scss';
import { Route, Switch, BrowserRouter as Router } from "react-router-dom";
import { Home, CreateSite, StatisticPage } from "./pages";
import io from "socket.io-client";

const App = props => {
   useEffect(() => {
       window.socket = io()
   }, []);
    return (
            <Switch>
                <Route path="/create_site">
                    <CreateSite />
                </Route>
                <Route path="/update_site">
                    <CreateSite />
                </Route>
                <Route path="/versions_statistic">
                    <StatisticPage />
                </Route>
                 <Route path="/">
                    <Home />
                </Route>
            </Switch>
    )
}

export default App;

ReactDOM.render(
    <Router>
        <App />
    </Router>,
    document.getElementById('app')
);