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

  state = {
    files: [
      'Drap n Drop.jpeg',
      'shit.jpg',
      'piss.png',
      'fuck.mp3',
      'landmine.doc'
    ]
  }

  handleDrop = (files) => {
    let fileList = this.state.files
    for (var i = 0; i < files.length; i++) {
      if (!files[i].name) return
      fileList.push(files[i].name)
    }
    this.setState({files: fileList})
  }

  render() {
    return (
      <div className="home-container">
        <DragDrop handleDrop={this.handleDrop}>
          <div style={{height: 300, width: 250}}>
            {this.state.files.map((file, index) =>
              <div key={index}>{file}</div>
            )}
          </div>
        </DragDrop>
      </div>

    )
  }
}

export default Home;
