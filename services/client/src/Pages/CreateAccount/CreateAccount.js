import React, { Component } from 'react';
import './CreateAccount.css';
import Home from '../Home/Home';
import { Link } from "react-router-dom";
import Input from '@material-ui/core/Input';
import axios from 'axios';

class CreateAccount extends Component {
  constructor(props){
    super(props);
    this.state = {
      username: null,
      email: null
    };

  }
  submitCreds = (e) => {
    var credentialJSON = {
      username: this.state.username, email: this.state.email
    };
      axios.post('http://localhost:5001/users', credentialJSON, {
          headers: {
            'Content-Type': 'application/json'
          }
      });
  }

  setUsername = (event) => {
    this.setState({
      username: event.target.value
    })
  }

  setEmail = (event) => {
    this.setState({
      email: event.target.value
    })
  }

  render() {
    return (
      <div className = "login-container">

        <Input placeholder = "Username" className = "login" onChange={(e) => this.setUsername(e)}/>
        <Input placeholder = "Email" className = "login" onChange={(e) => this.setEmail(e)} />

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
