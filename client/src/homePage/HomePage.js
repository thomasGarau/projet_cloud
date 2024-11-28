import React, { useState } from 'react';
import Navbar from '../component/navBar/NavBar';
import RecentFiles from '../component/section/RecentFiles';
import SharedWithMe from '../component/section/SharedWithMe';
import StorageInfo from '../component/section/StorageInfo';
import AllFiles from '../component/section/AllFiles';
import AddFileModal from '../component/modal/AddFileModal';
import RenameModal from '../component/modal/RenameModal';
import DeleteModal from '../component/modal/DeleteModal';
import ShareModal from '../component/modal/ShareModal';
import LoadingIndicator from '../component/loader/LoadingIndicator';
import './homePage.css';
import { useFileService } from '../API/FileServiceAPI';
import { getMimeTypes } from '../services/FileService';
import { generateFileID } from '../services/FileService';
import { decompresseFile } from '../services/Decompression';

const sectionComponents = {
  recent: RecentFiles,
  shared: SharedWithMe,
  storage: StorageInfo,
  allFiles: AllFiles,
};

const HomePage = () => {
  const [selectedSection, setSelectedSection] = useState('allFiles');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [showAddFileModal, setShowAddFileModal] = useState(false);
  const [showRenameModal, setShowRenameModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [isAddFileModalOpen, setIsAddFileModalOpen] = useState(false);
  const [refreshFiles, setRefreshFiles] = useState(false);
  const [uploadingFiles, setUploadingFiles] = useState([]);

  const { fetchUserFile, renameFile, deleteFile, uploadFile, shareFile, stopSharingFile, checkUploadStatus } = useFileService();

  const handleSearchChange = (e) => setSearchQuery(e.target.value);

  const openFile = async (fileName, extension) => {
    try {
        // Récupérer l'URL SAS pour le fichier depuis le serveur
        const fileUrl = await fetchUserFile(fileName, extension);

        // Extraire le nom du fichier depuis l'URL
        const urlPath = new URL(fileUrl).pathname;
        const blobName = urlPath.substring(urlPath.lastIndexOf("/") + 1);

        // Détecter si le fichier est compressé
        const isCompressed = blobName.includes("_compressed.bin");

        // Télécharger le fichier depuis Azure
        const response = await fetch(fileUrl);
        const arrayBuffer = await response.arrayBuffer();

        // Si le fichier est compressé, le décompresser
        let fileContent = arrayBuffer;
        let finalExtension = extension;

        if (isCompressed) {
            const { contenuDecode: decompressedContent, extensionOriginale } = decompresseFile(arrayBuffer);
            fileContent = decompressedContent;
            finalExtension = `.${extensionOriginale}`.replace(".", "").toLowerCase();
        }

        // Déterminer le type MIME du fichier
        const mimeTypes = getMimeTypes();
        const blobType = mimeTypes[finalExtension.split('.')[1]] || "application/octet-stream";
        console.log("extension", finalExtension);
        console.log("Type MIME du fichier :", blobType);

        // Créer un Blob pour ouvrir le fichier dans un nouvel onglet
        const blob = new Blob([fileContent], { type: blobType });
        const url = window.URL.createObjectURL(blob);
        window.open(url, "_blank");
    } catch (error) {
        console.error("Erreur lors de l'ouverture du fichier :", error);
    }
};


  const handleOpenAddFileModal = () => setShowAddFileModal(true);
  const handleCloseAddFileModal = () => setShowAddFileModal(false);

  const handleOpenRenameModal = (file) => {
    setSelectedFile(file);
    setShowRenameModal(true);
  };

  const handleOpenDeleteModal = (file, isShared = false) => {
    setSelectedFile(file);
    setShowDeleteModal(true);
  };

  const handleOpenShareModal = (file) => {
    setSelectedFile(file);
    setShowShareModal(true);
  };

  const handleCloseDeleteModal = () => setShowDeleteModal(false);
  const handleCloseShareModal = () => setShowShareModal(false);
  const handleCloseRenameModal = () => setShowRenameModal(false);


  const handleRenameSuccess = () => {
    setRefreshFiles(prev => !prev);
    handleCloseRenameModal();
  };
  
  const handleDeleteSuccess = () => {
    setRefreshFiles(prev => !prev);
    handleCloseDeleteModal();
  };

  const handleLoadingFile = (fileName, isLoading) => {
    console.log("Loading file : ", fileName, isLoading);
    if (isLoading) {
      setUploadingFiles(prev => [...prev, fileName]);
    } else {
      setUploadingFiles(prev => prev.filter(file => file !== fileName));
    }
  };

  const handleFileUpload = (file) => {
    const file_id = generateFileID();
    uploadFile(file, file_id, 
        () => handleLoadingFile(file.name, true),
        () => { 
            const checkInterval = setInterval(() => {
                checkUploadStatus(file_id, checkInterval, () => {
                    handleLoadingFile(file.name, false);
                    setRefreshFiles(prev => !prev);
                });
            }, 2500);
        }, 
        (error) => {
            handleLoadingFile(file.name, false);
            console.error('Upload failed', error);
        }
    );
  };


  const SectionComponent = sectionComponents[selectedSection];
  return (
    <div className="homePage">
      <Navbar />
      {uploadingFiles.length > 0 && <LoadingIndicator files={uploadingFiles} />}
      {isAddFileModalOpen && (
        <AddFileModal
            onClose={() => setIsAddFileModalOpen(false)}
            onUpload={(file) => handleFileUpload(file)}
            onLoadingFile={handleLoadingFile}
        />
      )}
      <div className="sidebar">
        <ul>
          <li
            className={selectedSection === 'allFiles' ? 'selected' : ''}
            onClick={() => setSelectedSection('allFiles')}
          >
            All Files
          </li>
          <li
            className={selectedSection === 'recent' ? 'selected' : ''}
            onClick={() => setSelectedSection('recent')}
          >
            Recent Files
          </li>
          <li
            className={selectedSection === 'shared' ? 'selected' : ''}
            onClick={() => setSelectedSection('shared')}
          >
            Shared With Me
          </li>
          <li
            className={selectedSection === 'storage' ? 'selected' : ''}
            onClick={() => setSelectedSection('storage')}
          >
            Storage
          </li>
          <li onClick={() => setIsAddFileModalOpen(true)}>Add Files</li>
        </ul>
      </div>
      <div className="main-content">
        <div className="search-bar">
          <input type="text" placeholder="Search files..." value={searchQuery} onChange={handleSearchChange} />
        </div>
        <div className="content">
        <SectionComponent
          searchQuery={searchQuery}
          openFile={openFile}
          handleOpenRenameModal={handleOpenRenameModal}
          handleOpenDeleteModal={handleOpenDeleteModal}
          handleOpenShareModal={handleOpenShareModal}
          refreshFiles={refreshFiles}
          setRefreshFiles={setRefreshFiles}
          onLoadingFile={handleLoadingFile}
        />

          {showAddFileModal && (
            <AddFileModal onClose={handleCloseAddFileModal}/>
          )}
          {showRenameModal && selectedFile && (
            <RenameModal
              onClose={handleCloseRenameModal}
              fileName={selectedFile.name}
              fileExtension={selectedFile.extension}
              onRename={(name, newName) => {
                renameFile(name, newName + selectedFile.extension)
                .then(handleRenameSuccess)
                .catch(error => console.error("Erreur lors du renommage : ", error));

              }}
            />
          )}

          {showDeleteModal && selectedFile && (
            <DeleteModal
              onClose={handleCloseDeleteModal}
              fileName={selectedFile.name}
              isSharedFile={selectedSection === 'shared'}
              onConfirm={(isSharedFile) => {
                if (isSharedFile) {
                  stopSharingFile(selectedFile.name, selectedFile.extension)
                    .then(handleDeleteSuccess)
                    .catch(error => console.error("Erreur lors de l'arrêt du partage : ", error));
                } else {
                  deleteFile(selectedFile.name, selectedFile.extension)
                    .then(handleDeleteSuccess)
                    .catch(error => console.error("Erreur lors de la suppression : ", error));
                }
              }}
            />
          )}

          {
            showShareModal && selectedFile && (
              <ShareModal
                onClose={handleCloseShareModal}
                fileName={selectedFile.name}
                fileExtension={selectedFile.extension}
                onShare={(sharedFileName, username) => {
                  shareFile(sharedFileName, username)
                    .then(() => {
                      console.log("Fichier partagé avec succès");
                    })
                    .catch(error => console.error("Erreur lors du partage : ", error));
                }}
              />
          )}
        </div>
      </div>
    </div>
)};
export default HomePage;
