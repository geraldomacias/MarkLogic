
import React, { Component } from 'react';
import axios from 'axios';

class FileUpload extends Component {
  constructor () {
    super();
    this.state = {
      file: null
    };
  }

  submitFile = (event) => {
    event.preventDefault();
    const formData = new FormData();
    formData.append('file', this.state.file[0]);
    axios.get('/upload', {
        params: {
            // hard coded test params for now
            file_name: "Basic_Stats.csv",
            user_id: 12345,
            bucket_name: "uploads" | "classified"
        }
      })
      .then(function (response) {
        console.log(response);
      })
      .catch(function (error) {
        console.log(error);
      });
  }

  handleFileUpload = (event) => {
    this.setState({file: event.target.files});
  }

  render () {
    return (
      <form onSubmit={this.submitFile}>
        <input label='upload file' type='file' onChange={this.handleFileUpload} />
        <button type='submit'>Upload</button>
      </form>
    );
  }
}

export default FileUpload;