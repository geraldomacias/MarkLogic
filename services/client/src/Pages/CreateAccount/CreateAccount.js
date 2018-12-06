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
    var credentialJSON = [{
      username: null, email: null
    }];
      axios.post('http://localhost:3000/users', credentialJSON, {
          headers: {
            'Content-Type': 'multipart/form-data'
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
