import React, { useState } from 'react';
import './shareModal.css';

const ShareModal = ({ onClose, onShare, fileName, fileExtension }) => {
  const [username, setUsername] = useState('');

    const handleShare = () => {
        onShare(fileName, username);
        onClose();
    };

  return (
    <div className="rename-modal-overlay">
      <div className="rename-modal">
        <h3>Partager le fichier</h3>
        <input
          type="text"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          placeholder="Nom d'utilisateur"
          className="share-input"
        />
        <div className="modal-actions">
          <button className="modal-action-confirm" onClick={handleShare}>Partager</button>
          <button className="modal-action-cancel" onClick={onClose}>Annuler</button>
        </div>
      </div>
    </div>
  );
};

export default ShareModal;
