import React from 'react';
import './fileOptionMenu.css';
import { useFileService } from '../../API/FileServiceAPI';
import { useState } from 'react';


const FileOptionsMenu = ({ onClose, fileName, fileExtension, onRenameRequested, onDeleteRequested, onShareRequested,  onOpenFile }) => {
  const { fetchUserFile, deleteFile } = useFileService();
 
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
      <button onClick={onOpenFile}>Ouvrir</button>
      <button onClick={onShareRequested}>Partager</button>
      <button onClick={onRenameRequested}>Renommer</button>
      <button onClick={onDeleteRequested}>Supprimer</button>
      <button onClick={downloadFile}>Télécharger</button>
    </div>
  );
};

export default FileOptionsMenu;