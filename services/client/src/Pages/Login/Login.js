import React, { Component } from 'react';
import './Login.css';
import Home from '../Home/Home';
import { Link } from "react-router-dom";

class Login extends Component {
  render() {
    return (
      <div className = "login-container">
        <img className= "image" alt="logo" src = "https://images.g2crowd.com/uploads/product/image/social_landscape/social_landscape_1489696751/marklogic.jpg"></img>
        <div className = "login-text">Username</div>
        <input className = "login username"></input>
        <div className = "login-text">Email</div>
        <input className = "login password"></input>
        <Link to="/Home">
          <button type = "button" className = "submit">
            Submit
          </button>
        </Link>
        <div className = "footer">dont have an account?</div>
      </div>
    );
  }
}

export default Login;
