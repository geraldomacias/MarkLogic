import React, { Component } from 'react';
import './Login.css';
import axios from 'axios';

class Login extends Component {
  constructor() {
    super();
  }
  getUsers() {
    axios.get(`${process.env.REACT_APP_USERS_SERVICE_URL}/users`)
    .then((res) => { console.log(res); })
    .catch((err) => { console.log(err); });
  }
  
  render() {
    return (
      <div className = "login-container">
        <img className= "image" alt="logo" src = "https://images.g2crowd.com/uploads/product/image/social_landscape/social_landscape_1489696751/marklogic.jpg"></img>
        <div className = "login-text">Username</div>
        <input className = "login username"></input>
        <div className = "login-text">Email</div>
        <input className = "login password"></input>
        <button className = "submit">Submit</button>
        <div className = "footer">dont have an account?</div>
      </div>
    );
  }
}

export default Login;
