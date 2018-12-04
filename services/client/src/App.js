import React, { Component } from 'react';
import './App.css';
import Login from './Pages/Login/Login';
import Home from './Pages/Home/Home';
import CreateAccount from './Pages/CreateAccount/CreateAccount';
import axios from 'axios';
import { BrowserRouter as Router, Route, Link } from "react-router-dom";

class App extends Component {
  constructor() {
    super();
    this.getUsers();
  }
  getUsers() {
    axios.get(`${process.env.REACT_APP_USERS_SERVICE_URL}users`)
    .then((res) => { console.log(res); })
    .catch((err) => { console.log(err); });
  }

  render() {
    return (
      <Router>
        <div className="App">
          <header className="App-header">
            <Route path="/" exact component={Login} />
            <Route path="/Home/" component={Home} />
            <Route path="/newAccount/" component={CreateAccount} />
          </header>
        </div>

      </Router>


    );
  }
}

export default App;
