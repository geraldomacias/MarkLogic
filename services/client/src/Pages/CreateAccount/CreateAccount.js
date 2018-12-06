import React, { Component } from 'react';
import './CreateAccount.css';
import Home from '../Home/Home';
import { Link } from "react-router-dom";
import Input from '@material-ui/core/Input';
import axios from 'axios';

class CreateAccount extends Component {
  constructor(props){
    super(props);
  }
  submitCreds = (e) => {
    var credentialJSON = {
      username: 'myarmo', email: 'mattyarmo@gmail.com'
    };
      axios.post('http://localhost:5001/users', credentialJSON, {
          headers: {
            'Content-Type': 'application/json'
          }
      });
  }

  render() {
    return (
      <div className = "login-container">

        <Input placeholder = "Username" className = "login"/>
        <Input placeholder = "Email" className = "login"/>

        <button onClick={(e) => this.submitCreds(e)} className="login">
          Sign Up
        </button>


        <div className = "footer">
          Already have an Account?
          <Link to="/">Login</Link>
        </div>
      </div>
    );
  }
}

export default CreateAccount;
