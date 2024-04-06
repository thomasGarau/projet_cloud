import React, { useState } from 'react';
import './addFileModale.css';

const AddFileModal = ({ onClose, onUpload }) => {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (e) => {
    setSelectedFile(e.target.files[0]);
  };

  const handleUpload = () => {
    if (selectedFile) {
      onUpload(selectedFile);
      onClose();
    }
  };

  return (
    <div className="modal-backdrop">
      <div className="modal-content">
        <h2>Upload File</h2>
        <input type="file" onChange={handleFileChange} />
        <button onClick={handleUpload}>Upload</button>
        <button onClick={onClose}>Close</button>
      </div>
    </div>
  );
};

export default AddFileModal;
