import React, { Component } from 'react'
import './DragDrop.css';


// tutorial pulled from:
// https://medium.com/@650egor/simple-drag-and-drop-file-upload-in-react-2cb409d88929
//

class DragDrop extends Component {

    dropRef = React.createRef()

    state = {
        dragging: false
    }

    handleDrop = (e) => {
        e.preventDefault()
        e.stopPropagation()
        this.setState({drag: false})
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
            this.props.handleDrop(e.dataTransfer.files)
            e.dataTransfer.clearData()
            this.dragCounter = 0
        }
    }

    handleDrag = (e) => {
        e.preventDefault()
        e.stopPropagation()
    }
    handleDragIn = (e) => {
        e.preventDefault()
        e.stopPropagation()
        this.dragCounter++
        if (e.dataTransfer.files && e.dataTransfer.files.length > 0){
            this.setState({dragging: true})
        }
    }

    handleDragOut = (e) => {
        e.preventDefault()
        e.stopPropagation()
        this.dragCounter--
        this.setState({dragging: false})
    }

    handleDragOver = (e) => {
        e.preventDefault()
        e.stopPropagation()
    }

    componentDidMount() {
        this.dragCounter = 0
        let div = this.dropRef.current
        div.addEventListener('dragenter', this.handleDragIn)
        div.addEventListener('dragleave', this.handleDragOut)
        div.addEventListener('dragover', this.handleDragOver)
        div.addEventListener('drop', this.handleDrop)
    }

    componentWillUnmount() {
        let div = this.dropRef.current
        div.removeEventListener('dragenter', this.handleDragIn)
        div.removeEventListener('dragleave', this.handleDragOut)
        div.removeEventListener('dragover', this.handleDragOver)
        div.removeEventListener('drop', this.handleDrop)
    }

    render() {
        return (
            <div
                style={{display: 'inline-block', position: 'relative'}}
                ref={this.dropRef}
            >
                {this.state.dragging &&
                 <div
                    style={{
                        border: 'dashed grey 4px',
                        backgroundColor: 'rgba(255,255,255,.8)',
                        position: 'absolute',
                        top: 0,
                        bottom: 0,
                        left: 0, 
                        right: 0,
                        zIndex: 9999
                    }}
                 >
                    <div
                        style={{
                        position: 'absolute',
                        top: '50%',
                        right: 0,
                        left: 0,
                        textAlign: 'center',
                        color: 'grey',
                        fontSize: 36
                        }}
                    >
                        <div>drop here :)</div>
                    </div>
                </div>
                }
                {this.props.children}
            </div>
        )
    }


}

export default DragDrop