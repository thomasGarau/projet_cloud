import React, { useState, useEffect, useRef } from 'react';
import { useFileService } from '../../API/FileServiceAPI';
import FileOptionModal from '../modal/FileOptionMenu';
import { getFileIcons } from '../../services/FileService';
import './recentFiles.css';



const Recent = ({openFile}) => {
  const { fetchRecentUserFilesInfo, fetchUserFile } = useFileService();
  const [recentFiles, setRecentFiles] = useState([]);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [selectedFileName, setSelectedFileName] = useState('');
  const [selectedFileExtension, setSelectedFileExtension] = useState('');
  const modalRef = useRef();

  const fileIcons = getFileIcons();

  useEffect(() => {
    const fetchFiles = async () => {
      try {
        const fetchedRecentFiles = await fetchRecentUserFilesInfo();
        setRecentFiles(fetchedRecentFiles);
      } catch (error) {
        console.error("Erreur lors de la récupération des fichiers récents: ", error);
      }
    };

    fetchFiles();
  }, []);

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
    setSelectedFile({...file, modalPosition: position});
    setSelectedFileName(file.name);
    setSelectedFileExtension(file.extension);
};


  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedFile(null);
    setSelectedFileName('');
    setSelectedFileExtension('');
  };

  return (
    <div className='table-container'>
      <table className='recent-table'>
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
          {recentFiles.map((file) => (
            <tr key={file.id} onClick={() => openFile(file.name, file.extension)}>
              <td><img src={fileIcons[file.extension.split('.')[1]] || fileIcons['default']} alt="file type" style={{ height: '30px' }}/></td>
              <td>{file.name}</td>
              <td>{new Date(file.lastOpened).toLocaleDateString()}</td>
              <td>{file.userName}</td>
              <td>
                <button onClick={(e) => handleOpenModal(e, file, openFile)}>⋮</button>
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
              fileName={selectedFileName}
              fileExtension={selectedFileExtension}
              onClose={handleCloseModal}
              onOpenFile={() => openFile(selectedFileName, selectedFileExtension)}
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default Recent;
