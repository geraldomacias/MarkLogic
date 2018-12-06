import React, { Component } from 'react';
import './Home.css';
import axios from 'axios';



class Home extends Component {
  constructor(props) {
    super(props);
    this.fileInput = React.createRef();
  }
  submitFiles = (e) => {
    var formData = new FormData();
    console.log(this.fileInput.current.files[0]);
    var csvFile = this.fileInput.current.files[0];
    if(csvFile != null) {
      formData.append("File", csvFile);
      axios.post('upload_file', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
      });
    }

  }

  render() {
    return (
      <div className = "home-container">
        <div>This is the home component</div>
        <input type="file" accept=".csv" ref={this.fileInput} />
        <button onClick = {(e) => this.submitFiles(e)} >submit</button>
      </div>
    );
  }
}

export default Home;
