import React, { useState, useEffect, useRef } from 'react';
import { useFileService } from '../../API/FileServiceAPI';
import FileOptionModal from '../modal/FileOptionMenu';
import { getFileIcons } from '../../services/FileService';
import './fileList.css';

const FileList = ({ fetchFilesFunction, openFile, handleOpenRenameModal, handleOpenDeleteModal, handleOpenShareModal, tableTitle }) => {
  const { fetchUserFile } = useFileService();
  const [files, setFiles] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const modalRef = useRef();
  const fileIcons = getFileIcons();

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const fetchedFiles = await fetchFilesFunction();
        setFiles(fetchedFiles);
      } catch (error) {
        console.error(`Erreur lors de la récupération des fichiers: ${error}`);
      }
    };
    fetchFiles();
  }, [fetchFilesFunction]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (modalRef.current && !modalRef.current.contains(event.target)) {
        setIsModalOpen(false);
        setSelectedFile(null);
      }
    };

    if (isModalOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [isModalOpen]);

  const handleOpenModal = (e, file) => {
    e.stopPropagation();
    const buttonRect = e.currentTarget.getBoundingClientRect();
    const position = {
      top: buttonRect.bottom + window.scrollY,
      left: buttonRect.left + window.scrollX,
    };

    setIsModalOpen(true);
    setSelectedFile({ ...file, modalPosition: position });
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedFile(null);
  };

  return (
    <div className='table-container'>
      <h2>{tableTitle}</h2>
      <table className='file-list-table'>
        <thead>
          <tr>
            <th>Type</th>
            <th>Nom</th>
            <th>Dernière ouverture</th>
            <th>Propriétaire</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {files.map((file) => (
            <tr key={file.id}>
              <td><img src={fileIcons[file.extension.split('.')[1]] || fileIcons['default']} alt="file type" /></td>
              <td>{file.name}</td>
              <td>{file.lastOpened}</td>
              <td>{file.userName}</td>
              <td>
                <button onClick={(e) => handleOpenModal(e, file)}>⋮</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {isModalOpen && selectedFile && (
        <div style={{
          position: 'absolute',
          top: `${selectedFile.modalPosition.top}px`,
          left: `${selectedFile.modalPosition.left}px`,
          zIndex: 100
        }}>
          <div ref={modalRef}>
            <FileOptionModal
              fileName={selectedFile.name}
              fileExtension={selectedFile.extension}
              onOpenFile={() => openFile(selectedFile.name, selectedFile.extension)}
              onClose={handleCloseModal}
              onRenameRequested={() => handleOpenRenameModal(selectedFile)}
              onDeleteRequested={() => handleOpenDeleteModal({ name: selectedFile.name + selectedFile.extension})}
              onShareRequested={() => handleOpenShareModal({ name: selectedFile.name + selectedFile.extension })}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default FileList;
