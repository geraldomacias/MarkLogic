import React, { Component } from 'react';
import './App.css';
<<<<<<< Updated upstream
import Login from './Login'
class App extends Component {
=======
import Login from './Pages/Login/Login'
import axios from 'axios';

class App extends Component {
  constructor() {
    super();
    this.getUsers();
  }
  getUsers() {
    axios.get(`${process.env.REACT_APP_USERS_SERVICE_URL}/users`)
    .then((res) => { console.log(res); })
    .catch((err) => { console.log(err); });
  }

>>>>>>> Stashed changes
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <Login/>
        </header>
      </div>
    );
  }
}

export default App;
