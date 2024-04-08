import React, { useState } from 'react';
import './renameModal.css';

const RenameModal = ({ onClose, onRename, fileName, fileExtension }) => {
  const [newName, setNewName] = useState('');

    const handleRename = () => {
        onRename(fileName + fileExtension, newName);
        onClose();
    };

  return (
    <div className="rename-modal-overlay">
      <div className="rename-modal">
        <h3>Renommer le fichier</h3>
        <input
          type="text"
          value={newName}
          onChange={(e) => setNewName(e.target.value)}
          placeholder="Nouveau nom"
          className="rename-input"
        />
        <div className="modal-actions">
          <button className="modal-action-confirm" onClick={handleRename}>Renommer</button>
          <button className="modal-action-cancel" onClick={onClose}>Annuler</button>
        </div>
      </div>
    </div>
  );
};

export default RenameModal;
