import React, { useState, useEffect } from 'react';
import { useFileService } from '../../API/FileServiceAPI';
import './localSync.css';

const LocalSync = () => {
  const [localPath, setLocalPath] = useState('');
  const [scriptGenerated, setScriptGenerated] = useState(false);
  const [error, setError] = useState('');
  const [isDirectoryPickerSupported, setIsDirectoryPickerSupported] = useState(false);
  const { generateSyncScript } = useFileService();

  // Vérifie si `showDirectoryPicker` est supporté
  useEffect(() => {
    setIsDirectoryPickerSupported('showDirectoryPicker' in window);
  }, []);

  const handlePathSelection = async () => {
    try {
      if (!isDirectoryPickerSupported) {
        setError('Votre navigateur ne supporte pas la sélection de dossiers.');
        return;
      }
      const directoryHandle = await window.showDirectoryPicker();
      console.log("Dossier sélectionné :", directoryHandle.name);
      setLocalPath(directoryHandle.name); // Utilise le nom du dossier sélectionné
      setError('');
    } catch (err) {
      console.error("Erreur lors de la sélection du dossier :", err);
      setError('Impossible de sélectionner le dossier.');
    }
  };

  const handleGenerateScript = async () => {
    try {
      if (!localPath) {
        setError('Veuillez entrer ou sélectionner un chemin valide.');
        return;
      }
      setError('');
      const response = await generateSyncScript(localPath);
      const blob = new Blob([response], { type: 'application/octet-stream' });
      const downloadLink = document.createElement('a');
      downloadLink.href = URL.createObjectURL(blob);
      downloadLink.download = 'sync_script.ps1';
      downloadLink.click();
      setScriptGenerated(true);
    } catch (err) {
      console.error("Erreur lors de la génération du script :", err);
      setError("Une erreur est survenue lors de la génération du script.");
    }
  };

  const handleManualPath = (e) => {
    setLocalPath(e.target.value);
  };

  return (
    <div className="local-sync-container">
      <h2>Synchronisation locale</h2>
      <p className="info-text">
        Ce module vous permet de synchroniser un dossier local avec votre espace de stockage dans le cloud.
        Sélectionnez un dossier ou entrez le chemin manuellement si la sélection automatique n'est pas disponible.
      </p>

      {isDirectoryPickerSupported ? (
        <button className="select-button" onClick={handlePathSelection}>
          Sélectionner un dossier
        </button>
      ) : (
        <div>
          <label htmlFor="manual-path" className="manual-path-label">
            Entrez le chemin du dossier :
          </label>
          <input
            id="manual-path"
            type="text"
            placeholder="Exemple : C:\\Users\\NomUtilisateur\\MonDossier"
            value={localPath}
            onChange={handleManualPath}
            className="manual-path-input"
          />
        </div>
      )}

      {localPath && (
        <p className="selected-path">
          <strong>Dossier sélectionné :</strong> {localPath}
        </p>
      )}
      <button
        className={`generate-button ${!localPath ? 'disabled' : ''}`}
        onClick={handleGenerateScript}
        disabled={!localPath}
      >
        Générer le script de synchronisation
      </button>
      {error && <p className="error-message">{error}</p>}
      {scriptGenerated && (
        <p className="success-message">
          Script généré avec succès ! Téléchargez-le et exécutez-le pour démarrer la synchronisation.
          <br />
          <strong>Instructions :</strong> Cliquez droit sur le fichier téléchargé, puis sélectionnez 'Exécuter avec PowerShell'.
        </p>
      )}
    </div>
  );
};

export default LocalSync;
