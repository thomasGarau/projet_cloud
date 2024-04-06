import React from 'react';
import './fileOptionMenu.css';
import { useFileService } from '../../API/FileServiceAPI';
import { useState } from 'react';


const FileOptionsMenu = ({ onClose, fileName, fileExtension, onRenameRequested, onDeleteRequested }) => {
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showRenameModal, setShowRenameModal] = useState(false);
  const { fetchUserFile, deleteFile, renameFile } = useFileService();

  const confirmDelete = async () => {
    await deleteFile(fileName, fileExtension);
    onClose();
  };

  const confirmRename = async (oldName, newName) => {
    await renameFile(oldName, newName);
    onClose();
  };

  const openFile = async () => {
    try {
        const fileData = await fetchUserFile(fileName, fileExtension);
        const blob = new Blob([fileData], { type: 'application/pdf' });
        const url = window.URL.createObjectURL(blob);
        window.open(url, '_blank');
        onClose();
    } catch (error) {
        console.error("Erreur lors de l'ouverture du fichier : ", error);
    }
};

    const shareFile = () => {
      console.log('Partager le fichier:', fileName);
      onClose();
    };
  
  
    const downloadFile = async () => {
      try {
          const fileData = await fetchUserFile(fileName, fileExtension);
          const blob = new Blob([fileData], { type: 'application/pdf' });

          const url = window.URL.createObjectURL(blob);
  
          const a = document.createElement("a");
          document.body.appendChild(a);
          a.style = "display: none";
          a.href = url;
          a.download = `${fileName}.${fileExtension}`;
  
          a.click();
  
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);
  
          onClose();
      } catch (error) {
          console.error("Erreur lors du téléchargement du fichier : ", error);
      }
  };
    
  
  return (
    <div className="file-options-menu">
      <button onClick={openFile}>Ouvrir</button>
      <button onClick={shareFile}>Partager</button>
      <button onClick={onRenameRequested}>Renommer</button>
      <button onClick={onDeleteRequested}>Supprimer</button>
      <button onClick={downloadFile}>Télécharger</button>
    </div>
  );
};

export default FileOptionsMenu;