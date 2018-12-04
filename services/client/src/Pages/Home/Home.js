import React, { Component } from 'react';
import './Home.css';

class Home extends Component {
  render() {
    return (
      <div className = "home-container">
        <div>This is the home component</div>
        <input type="file">Upload</input>
      </div>
    );
  }
}

export default Home;
