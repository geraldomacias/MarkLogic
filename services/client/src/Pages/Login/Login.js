import React, { Component } from 'react';
import './Login.css';
import Home from '../Home/Home';
import { Link } from "react-router-dom";

class Login extends Component {
  render() {
    return (
      <div className = "login-container">
        <input placeholder = "username" className = "login username"></input>
        <input placeholder = "Email" className = "login password"></input>
        <Link to="/Home" className = "submit" >
          Submit
        </Link>
        <div className = "footer">dont have an account?</div>
      </div>
    );
  }
}

export default Login;
