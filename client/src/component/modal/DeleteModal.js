import React from 'react';
import './deleteModal.css';

const DeleteModal = ({ onClose, onConfirm, fileName }) => {
  return (
    <div className="delete-modal-overlay">
      <div className="delete-modal">
        <h3>Confirmer la suppression</h3>
        <p>Voulez-vous vraiment supprimer le fichier <strong>{fileName}</strong> ?</p>
        <div className="modal-actions">
          <button className="modal-action-confirm" onClick={onConfirm}>Confirmer</button>
          <button className="modal-action-cancel" onClick={onClose}>Annuler</button>
        </div>
      </div>
    </div>
  );
};

export default DeleteModal;
