import React, { Component } from 'react';
import './Home.css';
import axios from 'axios';
import DragDrop from './../../Components/DragDrop/DragDrop';

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
      <div className="home-container">
        <DragDrop/>
      </div>

    )
  }
}

export default Home;
