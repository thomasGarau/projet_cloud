import React, { useState, useEffect } from 'react';
import Fuse from 'fuse.js';

import './allFiles.css';
import { useFileService } from '../../API/FileServiceAPI';
import FileOptionModal from '../modal/FileOptionMenu';
import RenameModal from '../modal/RenameModal';
import DeleteModal from '../modal/DeleteModal';
import { getFileIcons } from '../../services/FileService';


const AllFiles = ({searchQuery, openFile}) => {
  const { uploadFile, fetchUserFilesInfo, deleteFile, renameFile, fetchUserFile } = useFileService();
  const [files, setFiles] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [showRenameModal, setShowRenameModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedFileName, setSelectedFileName] = useState('');
  const [selectedFileExtension, setSelectedFileExtension] = useState('');
  const [modalPosition, setModalPosition] = useState({ top: 0, left: 0 });
  const [filteredFiles, setFilteredFiles] = useState(files);

  const fileIcons = getFileIcons(); 

  useEffect(() => {
    const fetchData = async () => {
      try {
        const fetchedFiles = await fetchUserFilesInfo();
        setFiles(fetchedFiles);
      } catch (error) {
        console.error("Erreur lors de la récupération des fichiers : ", error);
      }
    };
    fetchData();
  }, []);

  const fuseOptions = {
    includeScore: true,
    keys: ['name', 'extension'],
  };
  const fuse = new Fuse(files, fuseOptions);


  useEffect(() => {
    if (searchQuery) {
      const results = fuse.search(searchQuery).map(result => result.item);
      setFilteredFiles(results);
    } else {
      setFilteredFiles(files);
    }
  }, [searchQuery, files]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      const modal = document.querySelector('.file-option-modal');
      if (modal && !modal.contains(event.target)) {
        handleCloseModal();
      }
    };
  
    if (isModalOpen) {
      document.addEventListener('click', handleClickOutside);
    }
  
    return () => {
      document.removeEventListener('click', handleClickOutside);
    };
  }, [isModalOpen]);

   const fetchData = async () => {
    try {
      const fetchedFiles = await fetchUserFilesInfo();
      setFiles(fetchedFiles);
    } catch (error) {
      console.error("Erreur lors de la récupération des fichiers : ", error);
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      uploadFile(file).then(() => {
        console.log('Fichier téléchargé avec succès');
        fetchData();
      });
    }
  };

  const handleOpenOptionModal = (e, fileName, extension) => {
    e.preventDefault();
    const buttonRect = e.currentTarget.getBoundingClientRect();
    const containerRect = document.querySelector('.files-container').getBoundingClientRect();

    const position = {
      top: buttonRect.bottom - containerRect.top + window.scrollY,
      left: buttonRect.left - containerRect.left + window.scrollX,
    };

    setSelectedFileName(fileName);
    setSelectedFileExtension(extension);
    setModalPosition(position);
    setIsModalOpen(true);
  };

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setShowRenameModal(false);
    setShowDeleteModal(false);
    setSelectedFileName('');
    setSelectedFileExtension('');
  };

  const handleRename = () => {
    setShowRenameModal(true);
    setIsModalOpen(false);
  };

  const handleDelete = () => {
    setShowDeleteModal(true);
    setIsModalOpen(false);
  };

  const closeRenameModal = () => setShowRenameModal(false);
  const closeDeleteModal = () => setShowDeleteModal(false);

  return (
    <div className="files-container" onDragOver={handleDragOver} onDrop={handleDrop}>
      {filteredFiles.map((file) => (
        <div className="file-card" key={file.id} onClick={() => openFile(file.name, file.extension)}>
        <img src={fileIcons[file.extension.replace(/^\./, '')]} alt={file.extension} className="file-icon" />
        <div className="file-details">
          <h3 className="file-name">{file.name}</h3>
          <p className="file-info">{file.createdAt} par {file.userName}</p>
        </div>
        <button className="file-more" onClick={(e) => {
          e.stopPropagation();
          handleOpenOptionModal(e, file.name, file.extension);
        }}>⋮</button>
      </div>
      ))}
      {isModalOpen && (
        <div
          className="file-option-modal"
          style={{
            position: 'absolute',
            top: `${modalPosition.top}px`,
            left: `${modalPosition.left}px`,
            zIndex: 100
          }}
        >
          <FileOptionModal
            fileName={selectedFileName}
            fileExtension={selectedFileExtension}
            onOpenFile={() => openFile(selectedFileName, selectedFileExtension)}
            onClose={handleCloseModal}
            onRenameRequested={handleRename}
            onDeleteRequested={handleDelete}
            modalPosition={modalPosition}
          />
        </div>
      )}

      {showRenameModal && (
        <RenameModal
        onClose={closeRenameModal}
        onRename={(originalName, newName) => {
          renameFile(originalName, newName)
            .then(() => fetchData())
            .finally(() => closeRenameModal());
        }}
        fileName={selectedFileName}
        />
      )}
      {showDeleteModal && (
        <DeleteModal
          onClose={closeDeleteModal}
          onConfirm={() => {
            deleteFile(selectedFileName + selectedFileExtension)
              .then(() => fetchData())
              .finally(() => closeDeleteModal());
          }}
          fileName={selectedFileName}
        />
      )}
    </div>
  );
};

export default AllFiles;
