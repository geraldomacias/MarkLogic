import React, { Component } from 'react';
import './Login.css';
import Home from '../Home/Home';
import { Link } from "react-router-dom";
import Input from '@material-ui/core/Input';
import logo from './M.svg';
class Login extends Component {
  render() {
    return (
      <div className = "login-container">
        <img className="logo" src={logo}/>

        <Input placeholder = "Username" className = "login"/>
        <Input placeholder = "Email" className = "login"/>

        <Link to="/Home" className="submit">
          <div className="login-text">Submit</div>
        </Link>


        <div className = "footer">
          dont have an account?
          <Link to="/CreateAccount">Sign Up</Link>
        </div>
      </div>
    );
  }
}

export default Login;
