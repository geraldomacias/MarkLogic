import React, { Component } from 'react';
import './CreateAccount.css';
import Home from '../Home/Home';
import { Link } from "react-router-dom";
import Input from '@material-ui/core/Input';

class CreateAccount extends Component {
  render() {
    return (
      <div className = "login-container">

        <Input placeholder = "Username" className = "login"/>
        <Input placeholder = "Email" className = "login"/>

        <Link to="/Home" className="submit">
          <div className="login-text">Sign Up!</div>
        </Link>


        <div className = "footer">
          Already have an Account?
          <Link to="/">Login</Link>
        </div>
      </div>
    );
  }
}

export default CreateAccount;
